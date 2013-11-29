# coding=utf-8
try:
    import simplejson as json
except ImportError:
    import json
import six
from odin import resources

JSON_SUPPORTED_TYPES = six.string_types + (int, float, list, dict, tuple)


class JSRNEncoder(json.JSONEncoder):
    """
    Encoder for JSRN resources.
    """
    def default(self, o):
        if isinstance(o, resources.Resource):
            obj = {f.name: v if f.data_type in JSON_SUPPORTED_TYPES else f.to_string(v) for f, v in o.items() }
            obj[resources.RESOURCE_TYPE_FIELD] = o._meta.resource_name
            return obj
        return super(JSRNEncoder, self)


def build_object_graph(obj, resource_name=None):
    """
    From the decoded JSON structure, generate an object graph.

    :raises ValidationError: During building of the object graph and issues discovered are raised as a ValidationError.
    """

    if isinstance(obj, dict):
        return resources.create_resource_from_dict(obj, resource_name)

    if isinstance(obj, list):
        return [build_object_graph(o, resource_name) for o in obj]

    return obj


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
    return build_object_graph(json.loads(s), resource_name)


def dump(resource, fp, pretty_print=False):
    """
    Dump to a JSON encoded file.

    :param resource: The root resource to dump to a JSON encoded file.
    :param fp: The rile pointer that represents the output file.
    :param pretty_print: Pretty print the output, ie apply newline characters and indentation.
    """
    return json.dump(resource, fp, cls=JSRNEncoder, indent=4 if pretty_print else None)


def dumps(resource, pretty_print=True):
    """
    Dump to a JSON encoded string.

    :param resource: The root resource to dump to a JSON encoded file.
    :param pretty_print: Pretty print the output, ie apply newline characters and indentation.
    """
    return json.dumps(resource, cls=JSRNEncoder, indent=4 if pretty_print else None)
