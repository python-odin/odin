###############
Mapping Helpers
###############

Odin includes a few helpers to help defining mappings.

Defining Mappings
=================

When defining mappings using the shorthand mappings property these methods simplify the definition of mapping rules.
They also provide sensible defaults.

.. automodule:: odin.mapping
    :noindex:

    .. autofunction:: define

    .. autofunction:: assign


Action Helpers
==============

Predefined actions for use in mapping definitions.

.. automodule:: odin.mapping.helpers

    .. autofunction:: sum_fields

    .. autoclass:: JoinFields

    .. autoclass:: SplitField

    .. autoclass:: ApplyMapping


Special Mappers
===============

    .. autoclass:: NoOpMapper