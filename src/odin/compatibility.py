"""
This module is to include utils for managing compatibility between Python and Odin releases.
"""
import inspect
import warnings


def deprecated(message: str, category=DeprecationWarning):
    """Decorator for marking classes/functions as being deprecated and are to be removed in the future.

    :param message: Message provided.
    :param category: Category of warning, defaults to DeprecationWarning

    """

    def wrap(obj):
        if inspect.isclass(obj):
            old_init = obj.__init__

            def wrapped_init(*args, **kwargs):
                warnings.warn(
                    f"{obj.__name__} is deprecated and scheduled for removal. {message}",
                    category=category,
                    stacklevel=2,
                )
                return old_init(*args, **kwargs)

            obj.__init__ = wrapped_init
            return obj

        else:

            def wrapped_func(*args, **kwargs):
                warnings.warn(
                    f"{obj.__name__} is deprecated and scheduled for removal. {message}",
                    category=category,
                    stacklevel=2,
                )
                return obj(*args, **kwargs)

            return wrapped_func

    return wrap
