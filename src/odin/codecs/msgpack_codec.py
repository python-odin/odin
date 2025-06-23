"""Codec to load/save Message Pack (msgpack) documents."""

import datetime
import uuid
from typing import TextIO

try:
    import msgpack
except ImportError:
    raise ImportError(
        "odin.codecs.msgpack_codec requires the 'msgpack-python' package."
    ) from None  # noqa

from odin import ResourceAdapter, bases, resources, serializers

TYPE_SERIALIZERS = {
    datetime.date: serializers.date_iso_format,
    datetime.time: serializers.time_iso_format,
    datetime.datetime: serializers.datetime_iso_format,
    uuid.UUID: str,
}
CONTENT_TYPE = "application/x-msgpack"


class OdinPacker(msgpack.Packer):
    """Encoder for Odin resources."""

    def __init__(self, include_virtual_fields: bool = True, *args, **kwargs):
        kwargs.setdefault("default", self.default)
        super().__init__(*args, **kwargs)
        self.include_virtual_fields = include_virtual_fields

    def default(self, o):
        if isinstance(o, resources.ResourceBase | ResourceAdapter):
            return o.to_dict(self.include_virtual_fields, True)

        elif isinstance(o, bases.ResourceIterable):
            return list(o)

        elif o.__class__ in TYPE_SERIALIZERS:
            return TYPE_SERIALIZERS[o.__class__](o)


def load(
    fp: TextIO,
    resource: resources.ResourceBase = None,
    full_clean: bool = True,
    default_to_not_supplied: bool = False,
):
    """Load a from a MessagePack encoded file.

    See :py:meth:`loads` for more details of the loading operation.

    :param fp: a file pointer to read MessagePack data from.
    :param resource: A resource instance or a resource name to use as the base for
        creating a resource.
    :param full_clean: Do a full clean of the object as part of the loading process.
    :param default_to_not_supplied:
    :returns: A resource object or object graph of resources loaded from file.
    """
    return resources.build_object_graph(
        msgpack.load(fp), resource, full_clean, default_to_not_supplied
    )


def loads(
    s: str,
    resource: resources.ResourceBase = None,
    full_clean: bool = True,
    default_to_not_supplied: bool = False,
):
    """Load from a MessagePack encoded string/bytes.

    If a ``resource`` value is supplied it is used as the base resource for the
    supplied MessagePack data. I one is not supplied a resource type field ``$`` is
    used to obtain the type represented by the dictionary. A ``ValidationError``
    will be raised if either of these values are supplied and not compatible. It is
    valid for a type to be supplied in the file to be a child object from within the
    inheritance tree.

    :param s: String to load and parse.
    :param resource: A resource instance or a resource name to use as the base for
        creating a resource.
    :param full_clean: Do a full clean of the object as part of the loading process.
    :param default_to_not_supplied:
    :returns: A resource object or object graph of resources parsed from supplied
        string.
    """
    return resources.build_object_graph(
        msgpack.loads(s), resource, full_clean, False, default_to_not_supplied
    )


def dump(
    resource: resources.ResourceBase,
    fp: TextIO,
    cls=OdinPacker,
    include_virtual_fields: bool = True,
    **kwargs,
):
    """Dump to a MessagePack encoded file.

    :param include_virtual_fields:
    :param resource: The root resource to dump to a MessagePack encoded file.
    :param cls: Encoder to use serializing to a string; default is the
        :py:class:`OdinEncoder`.
    :param fp: The file pointer that represents the output file.
    """
    fp.write(cls(include_virtual_fields, **kwargs).pack(resource))


def dumps(
    resource: resources.ResourceBase,
    cls=OdinPacker,
    include_virtual_fields: bool = True,
    **kwargs,
):
    """Dump to a MessagePack encoded string.

    :param include_virtual_fields:
    :param resource: The root resource to dump to a MessagePack encoded file.
    :param cls: Encoder to use serializing to a string; default is the
        :py:class:`OdinEncoder`.
    :returns: MessagePack encoded string.
    """
    return cls(include_virtual_fields, **kwargs).pack(resource)
