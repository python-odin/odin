# -*- coding: utf-8 -*-
"""
Some helpful decorators.
"""
from odin.resources import build_object_graph


def returns_resource(func=None, resource=None, full_clean=True):
    """
    Apply to a function that returns a dictionary that should be converted into a resource (or resources).

    Note that this decorator can throw ``ValidationError`` exceptions.\

    :return: Resource, Array of resources or None.
    """
    def outer(func):  # noqa
        def inner(*args, **kwargs):
            return build_object_graph(func(*args, **kwargs), resource, full_clean)
        return inner

    return outer(func) if func else outer


def returns_resource_of_type(func=None, codec=None, resource=None, codec_opts=None):
    """
    Apply to a function that returns data that can be handled by a odin.codec to be converted into a resource (or
    resources).

    Note that this decorator can throw ``ValidationError`` exceptions.\

    :return: Resource, Array of resources or None.
    """
    def outer(func):  # noqa
        def inner(*args, **kwargs):
            data = func(*args, **kwargs)
            return codec.loads(data, resource, **(codec_opts or dict()))
        return inner

    return outer(func) if func else outer
