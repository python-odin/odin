__author__ = "Tim Savage"
__author_email__ = "tim.savage@poweredbypenguins.org"
__copyright__ = "Copyright (C) 2013 Tim Savage"
__version__ = "0.3.1"

try:
    import simplejson as json
except ImportError:
    import json
from odin.resources import Resource
from odin.fields import *
from odin.fields.composite import *


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
    from odin.encoding import build_object_graph
    if isinstance(resource, type) and issubclass(resource, Resource):
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
    from odin.encoding import JSRNEncoder
    return json.dump(resource, fp, cls=JSRNEncoder, indent=4 if pretty_print else None)


def dumps(resource, pretty_print=True):
    """
    Dump to a JSON encoded string.

    :param resource: The root resource to dump to a JSON encoded file.
    :param pretty_print: Pretty print the output, ie apply newline characters and indentation.
    """
    from odin.encoding import JSRNEncoder
    return json.dumps(resource, cls=JSRNEncoder, indent=4 if pretty_print else None)
