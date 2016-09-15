"""
This module is to include utils for managing compatibility between Python and Odin releases.
"""
import inspect
import warnings


def deprecated(message, category=DeprecationWarning):
    """
    Decorator for marking classes/functions as being deprecated and are to be removed in the future.

    :param message: Message provided.
    :param category: Category of warning, defaults to DeprecationWarning

    """
    def wrap(obj):
        if inspect.isclass(obj):
            old_init = obj.__init__

            def wrapped_init(*args, **kwargs):
                warnings.warn(
                    "{0} is deprecated and scheduled for removal. {1}".format(obj.__name__, message),
                    category=category
                )
                return old_init(*args, **kwargs)

            obj.__init__ = wrapped_init
            return obj

        else:
            def wrapped_func(*args, **kwargs):
                warnings.warn(
                    "{0} is deprecated and scheduled for removal. {1}".format(obj.__name__, message),
                    category=category
                )
                return obj(*args, **kwargs)

            return wrapped_func
    return wrap
