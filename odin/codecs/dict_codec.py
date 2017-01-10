import six
from odin import bases
from odin import resources, ResourceAdapter


TYPE_SERIALIZERS = {}


class OdinEncoder(object):
    def __init__(self, include_virtual_fields=True, include_type_field=True):
        self.include_virtual_fields = include_virtual_fields
        self.include_type_field = include_type_field

    def default(self, o):
        if isinstance(o, (resources.ResourceBase, ResourceAdapter)):
            obj = o.to_dict(self.include_virtual_fields)
            if self.include_type_field:
                obj[o._meta.type_field] = o._meta.resource_name
            return obj
        elif isinstance(o, bases.ResourceIterable):
            return list(o)
        elif o.__class__ in TYPE_SERIALIZERS:
            return TYPE_SERIALIZERS[o.__class__](o)
        return o

    def encode(self, o):
        _encoder = _make_encoder(self.default)
        return _encoder(o)


load = resources.build_object_graph
load.__doc__ = """
    Load a :py:class:`dict` into a Resource structure.

    This method is an alias of :py:func:`odin.

    :param d: Dict to load

    :param resource: A resource type, resource name or list of resources and names to use as the base for creating a
        resource. If a list is supplied the first item will be used if a resource type is not supplied.
    :raises ValidationError: During building of the object graph and issues discovered are raised as a ValidationError.

    """


def dump(resource, cls=OdinEncoder, **kwargs):
    """
    Dump a resource structure into a nested :py:class:`dict`.

    While a resource includes a *to_dict* method this method is not recursive. The dict codec recursively iterates
    through the resource structure to produce a full dict. This is useful for testing for example.

    :param resource: The root resource to dump
    :return:

    """
    encoder = cls(**kwargs)
    return encoder.encode(resource)


def _make_encoder(_default):
    def _encode_list(lst):
        return [_encode(o) for o in lst]

    def _encode_dict(dct):
        return dict((k, _encode(o)) for k, o in six.iteritems(dct))

    def _encode(o):
        if isinstance(o, (list, tuple)):
            return _encode_list(o)
        elif isinstance(o, dict):
            return _encode_dict(o)
        else:
            o = _default(o)
            if isinstance(o, (list, tuple, dict)):
                return _encode(o)
            return o
    return _encode
