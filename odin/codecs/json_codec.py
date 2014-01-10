# coding=utf-8
import datetime
from odin import serializers
from odin import resources

try:
    import simplejson as json
except ImportError:
    import json

JSON_TYPES = {
    datetime.datetime: serializers.datetime_ecma_format
}


class OdinEncoder(json.JSONEncoder):
    """
    Encoder for Odin resources.
    """

    def default(self, o):
        if isinstance(o, resources.Resource):
            obj = o.to_dict()
            obj[resources.RESOURCE_TYPE_FIELD] = o._meta.resource_name
            return obj
        elif o.__class__ in JSON_TYPES:
            return JSON_TYPES[o.__class__](o)
        else:
            return super(OdinEncoder, self)


def load(fp, *args, **kwargs):
    """
    Load a from a JSON encoded file.

    See ``loads`` for a complete explanation of other parameters and operation of this method.
    """
    return loads(fp.read(), *args, **kwargs)


def loads(s, resource=None):
    """
    Load from a JSON encoded string.

    If a ``resource`` value is supplied it is used as the base resource for the supplied JSON. I one is not supplied a
    resource type field ``$`` is used to obtain the type represented by the dictionary. A ``ValidationError`` will be
    raised if either of these values are supplied and not compatible. It is valid for a type to be supplied in the file
    to be a child object from within the inheritance tree.

    :param s: String to load and parse.
    :param resource: A resource instance or a resource name to use as the base for creating a resource.
    """
    if isinstance(resource, type) and issubclass(resource, resources.Resource):
        resource_name = resource._meta.resource_name
    else:
        resource_name = resource
    return resources.build_object_graph(json.loads(s), resource_name)


def dump(resource, fp, cls=OdinEncoder, **kwargs):
    """
    Dump to a JSON encoded file.

    :param resource: The root resource to dump to a JSON encoded file.
    :param fp: The rile pointer that represents the output file.
    """
    return json.dump(resource, fp, cls=cls, **kwargs)


def dumps(resource, cls=OdinEncoder, **kwargs):
    """
    Dump to a JSON encoded string.

    :param resource: The root resource to dump to a JSON encoded file.
    :param pretty_print: Pretty print the output, ie apply newline characters and indentation.
    """
    return json.dumps(resource, cls=cls, **kwargs)
