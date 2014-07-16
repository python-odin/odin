# -*- coding: utf-8 -*-
"""
Some helpful decorators.
"""
from odin.resources import build_object_graph


def returns_resource(func=None, codec=None, resource=None, full_clean=True, codec_opts=None):
    """
    Apply to a function that returns data that can be converted into a resource (or resources).

    If a codec is provided the data will be converted using the codec, if not it will be assumed that the supplied data
    is a dictionary that can be converted into a resource.

    Note that this decorator can throw ``ValidationError`` exceptions.

    :param codec: Codec that should be used to convert data.
    :param resource: Resource to convert to (only required if the data does not contain a resource identifier).
    :param full_clean: Perform a full clean on the data post conversion.
    :param codec_opts: Options that should be supplied ot the codec (in the form of a dictionary).

    :return: Resource, Array of resources or None.
    """
    def outer(func):  # noqa
        def inner(*args, **kwargs):
            data = func(*args, **kwargs)
            if codec:
                opts = codec_opts or {}
                opts.setdefault('full_clean', full_clean)
                return codec.loads(data, resource, **opts)
            else:
                return build_object_graph(data, resource, full_clean)
        return inner

    return outer(func) if func else outer
