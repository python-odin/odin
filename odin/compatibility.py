"""
This module is to include utils for managing compatibility between Python and Odin releases.
"""
from six import wraps


def deprecated(message):
    """
    Decorator for marking classes/functions as being deprecated and are to be removed in the future.

    :param message: Message provided.

    """
    def inner(fun):
        @wraps(fun)
        def wrapper(*args, **kwargs):
            import warnings
            warnings.warn("{} is deprecated and scheduled for removal. {}".format(fun.__name__, message))
            return fun(*args, **kwargs)
        return wrapper
    return inner
