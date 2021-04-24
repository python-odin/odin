# -*- coding: utf-8 -*-
from six import StringIO
from odin import bases
from odin import resources, ResourceAdapter
from odin.exceptions import CodecEncodeError
from odin.utils import getmeta

try:
    import yaml
except ImportError:
    raise ImportError(  # pragma: no cover
        "odin.codecs.yaml_codec requires the 'pyyaml' package."
    )

try:
    from yaml import CSafeLoader as SafeLoader, CSafeDumper as SafeDumper
except ImportError:
    from yaml import SafeLoader, SafeDumper  # pragma: no cover


YAML_TYPES = {}
CONTENT_TYPE = "application/x-yaml"


class OdinDumper(SafeDumper):
    def __init__(
        self,
        stream,
        include_virtual_fields=True,
        include_type_field=True,
        *args,
        **kwargs
    ):
        SafeDumper.__init__(self, stream, *args, **kwargs)
        self.include_virtual_fields = include_virtual_fields
        self.include_type_field = include_type_field

    def represent_resource(self, data):
        obj = data.to_dict(self.include_virtual_fields)
        if self.include_type_field:
            meta = getmeta(data)
            obj[meta.type_field] = meta.resource_name
        return self.represent_dict(obj)


OdinDumper.add_multi_representer(resources.ResourceBase, OdinDumper.represent_resource)
OdinDumper.add_multi_representer(ResourceAdapter, OdinDumper.represent_resource)
OdinDumper.add_multi_representer(bases.ResourceIterable, OdinDumper.represent_list)


def load(fp, resource=None, full_clean=True, default_to_not_supplied=False):
    """
    Load a resource from a YAML encoded file.

    If a ``resource`` value is supplied it is used as the base resource for the supplied YAML. I one is not supplied a
    resource type field ``$`` is used to obtain the type represented by the dictionary. A ``ValidationError`` will be
    raised if either of these values are supplied and not compatible. It is valid for a type to be supplied in the file
    to be a child object from within the inheritance tree.

    :param fp: a file pointer to read YAML data fromat.
    :param resource: A resource type, resource name or list of resources and names to use as the base for creating a
        resource. If a list is supplied the first item will be used if a resource type is not supplied.
    :param full_clean: Do a full clean of the object as part of the loading process.
    :param default_to_not_supplied: Used for loading partial resources. Any fields not supplied are replaced with
        NOT_SUPPLIED.
    :returns: A resource object or object graph of resources loaded from file.

    """
    # try:
    return resources.build_object_graph(
        #  The SafeLoader is used here, this is to allow for CSafeLoader to be used.
        yaml.load(fp, SafeLoader),  # nosec - B506:yaml_load
        resource,
        full_clean,
        False,
        default_to_not_supplied,
    )
    # except (ValueError, TypeError) as ex:
    #     raise CodecDecodeError(str(ex))


loads = load


def dump(resource, fp, dumper=OdinDumper, **kwargs):
    """
    Dump to a YAML encoded file.

    :param resource: The root resource to dump to a YAML encoded file.
    :param dumper: Dumper to use serializing to a string; default is the :py:class:`OdinDumper`.
    :param fp: The file pointer that represents the output file.

    """
    try:
        yaml.dump(resource, fp, Dumper=dumper, **kwargs)
    except ValueError as ex:
        raise CodecEncodeError(str(ex))


def dumps(resource, dumper=OdinDumper, **kwargs):
    """
    Dump to a YAML encoded string.

    :param resource: The root resource to dump to a YAML encoded file.
    :param dumper: Dumper to use serializing to a string; default is the :py:class:`OdinDumper`.
    :returns: YAML encoded string.

    """
    stream = StringIO()
    dump(resource, stream, dumper, **kwargs)
    return stream.getvalue()
