# -*- coding: utf-8 -*-
import datetime
from odin import serializers, resources, mapping
from odin.exceptions import CodecDecodeError, CodecEncodeError

try:
    import simplejson as json
except ImportError:
    import json

JSON_TYPES = {
    datetime.date: serializers.date_iso_format,
    datetime.time: serializers.time_iso_format,
    datetime.datetime: serializers.datetime_iso_format,
}
CONTENT_TYPE = 'application/json'


class OdinEncoder(json.JSONEncoder):
    """
    Encoder for Odin resources.
    """
    def __init__(self, include_virtual_fields=True, *args, **kwargs):
        super(OdinEncoder, self).__init__(*args, **kwargs)
        self.include_virtual_fields = include_virtual_fields

    def default(self, o):
        if isinstance(o, resources.Resource):
            obj = o.to_dict(self.include_virtual_fields)
            obj[o._meta.type_field] = o._meta.resource_name
            return obj
        elif isinstance(o, mapping.MappingResult):
            return list(o)
        elif o.__class__ in JSON_TYPES:
            return JSON_TYPES[o.__class__](o)
        return super(OdinEncoder, self)


def load(fp, resource=None, full_clean=True):
    """
    Load a from a JSON encoded file.

    See :py:meth:`loads` for more details of the loading operation.

    :param fp: a file pointer to read JSON data from.
    :param resource: A resource instance or a resource name to use as the base for creating a resource.
    :param full_clean: Do a full clean of the object as part of the loading process.
    :returns: A resource object or object graph of resources loaded from file.
    """
    return loads(fp.read(), resource, full_clean)


def loads(s, resource=None, full_clean=True):
    """
    Load from a JSON encoded string.

    If a ``resource`` value is supplied it is used as the base resource for the supplied JSON. I one is not supplied a
    resource type field ``$`` is used to obtain the type represented by the dictionary. A ``ValidationError`` will be
    raised if either of these values are supplied and not compatible. It is valid for a type to be supplied in the file
    to be a child object from within the inheritance tree.

    :param s: String to load and parse.
    :param resource: A resource instance or a resource name to use as the base for creating a resource.
    :param full_clean: Do a full clean of the object as part of the loading process.
    :returns: A resource object or object graph of resources parsed from supplied string.
    """
    try:
        return resources.build_object_graph(json.loads(s), resource, full_clean, copy_dict=False)
    except (ValueError, TypeError) as ex:
        raise CodecDecodeError(str(ex))


def dump(resource, fp, cls=OdinEncoder, include_virtual_fields=True, **kwargs):
    """
    Dump to a JSON encoded file.

    :param resource: The root resource to dump to a JSON encoded file.
    :param cls: Encoder to use serializing to a string; default is the :py:class:`OdinEncoder`.
    :param fp: The file pointer that represents the output file.
    """
    try:
        json.dump(resource, fp, cls=cls, include_virtual_fields=include_virtual_fields, **kwargs)
    except ValueError as ex:
        raise CodecEncodeError(str(ex))


def dumps(resource, cls=OdinEncoder, include_virtual_fields=True, **kwargs):
    """
    Dump to a JSON encoded string.

    :param resource: The root resource to dump to a JSON encoded file.
    :param cls: Encoder to use serializing to a string; default is the :py:class:`OdinEncoder`.
    :returns: JSON encoded string.
    """
    try:
        return json.dumps(resource, cls=cls, include_virtual_fields=include_virtual_fields, **kwargs)
    except ValueError as ex:
        raise CodecEncodeError(str(ex))
