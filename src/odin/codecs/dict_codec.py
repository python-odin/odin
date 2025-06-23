from odin import ResourceAdapter, bases, resources

TYPE_SERIALIZERS = {}


class OdinEncoder:
    def __init__(self, include_virtual_fields=True, include_type_field=True):
        self.include_virtual_fields = include_virtual_fields
        self.include_type_field = include_type_field

    def default(self, o):
        if isinstance(o, resources.ResourceBase | ResourceAdapter):
            return o.to_dict(self.include_virtual_fields, self.include_type_field)
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

    :param resource: A resource type, resource name or list of resources and names to
        use as the base for creating a resource. If a list is supplied the first item
        will be used if a resource type is not supplied.
    :raises ValidationError: During building of the object graph and issues discovered
        are raised as a ValidationError.

    """


def dump(resource, cls=OdinEncoder, **kwargs):
    """
    Dump a resource structure into a nested :py:class:`dict`.

    While a resource includes a *to_dict* method this method is not recursive. The dict
    codec recursively iterates through the resource structure to produce a full dict.
    This is useful for testing for example.

    :param resource: The root resource to dump
    :param cls: Encoder class to utilise
    :return:

    """
    encoder = cls(**kwargs)
    return encoder.encode(resource)


def _make_encoder(_default):
    def _encode_list(lst):
        return [_encode(o) for o in lst]

    def _encode_dict(dct):
        return {k: _encode(o) for k, o in dct.items()}

    def _encode(o):
        if isinstance(o, list | tuple):
            return _encode_list(o)
        elif isinstance(o, dict):
            return _encode_dict(o)
        else:
            o = _default(o)
            if isinstance(o, list | tuple | dict):
                return _encode(o)
            return o

    return _encode
