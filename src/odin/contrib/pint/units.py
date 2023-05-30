try:
    from pint import UnitRegistry
except ImportError:
    raise ImportError(
        "The pint package is not installed, please install this library to use quantity fields."
    ) from None

# Common unit registry
registry = UnitRegistry()
