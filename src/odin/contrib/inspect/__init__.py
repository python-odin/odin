import warnings
warnings.warn(message="This is a ALPHA that is a work in progress (only works with Python 3).")


# Check required libraries are installed
def import_check():
    try:
        import humanfriendly  # noqa
    except ImportError:
        raise ImportError("The `humanfriendly` library is required to use the inspector.")


import_check()
