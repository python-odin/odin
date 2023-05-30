"""Helpful decorators."""
from typing import Any, Callable, Dict, Type, TypeVar, Union

from odin.resources import ResourceBase, build_object_graph

_F = TypeVar("_F", bound=Callable[..., Any])


def returns_resource(
    func: _F = None,
    codec=None,
    resource: Type[ResourceBase] = None,
    full_clean: bool = True,
    codec_opts: Dict[str, Any] = None,
) -> Union[_F, Callable[[_F], _F]]:
    """Apply to a function that returns data that can be converted into a resource (or resources).

    If a codec is provided the data will be converted using the codec, if not it will be assumed that the supplied data
    is a dictionary that can be converted into a resource.

    Note that this decorator can raise ``ValidationError`` exceptions.

    :param func: Function being wrapped
    :param codec: Optional codec that should be used to convert data.
    :param resource: Optional resource to convert to (only required if the data does not contain a resource identifier).
    :param full_clean: Perform a full clean on the data post conversion.
    :param codec_opts: Options that should be supplied ot the codec.

    :return: Resource, Array of resources or None.
    """

    def outer(func):  # noqa
        def inner(*args, **kwargs):
            data = func(*args, **kwargs)
            if codec:
                opts = codec_opts or {}
                opts.setdefault("full_clean", full_clean)
                return codec.loads(data, resource, **opts)
            else:
                return build_object_graph(data, resource, full_clean)

        return inner

    return outer(func) if func else outer
