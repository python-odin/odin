###############
Mapping Classes
###############

A mapping is a utility class that defines how data is mapped between resources.

The basics:
 * Each mapping is a Python class that subclasses :py:class:`odin.Mapping`.
 * Each mapping defines a ``from_resource`` and a ``to_resource``
 * Parameters and decorated methods define rules for mapping between resources.

