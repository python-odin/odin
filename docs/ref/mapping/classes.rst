###############
Mapping Classes
###############

A mapping is a utility class that defines how data is mapped between objects, these objects are typically
:class:`odin.Resource` but other Python objects can be supported.

The basics:
 * Each mapping is a Python class that subclasses :py:class:`odin.Mapping`.
 * Each mapping defines a ``from_obj`` and a ``to_obj``
 * Parameters and decorated methods define rules for mapping between objects.


Defining a Mapping
==================

``from_obj`` and ``to_obj``
---------------------------

These attributes specify the source and destination of the mapping operation and must be defined to for a mapping to be
considered valid.

.. note:: For an object to be successfully mapped it's fields need to be known. This is handled by a ``FieldResolver``
    instance.

Example::

    class AuthorToNewAuthor(odin.Mapping):
        from_obj = Author
        to_obj = NewAuthor


Auto generated mappings
-----------------------

When a field of the same name exists on both the from and to objects an automatic mapping is created. If no data
transformation or data type conversion is needed no further work is required. The mappings will be automatically
created.

You can exclude fields from automatic generation by; including the field in the ``exclude_fields`` :py:meth:`list` (or
:py:meth:`tuple`). Fields are also excluded from automatic generation when they are specified as a target by any other
mapping rule.

Fields that defined relationships (eg :class:`DictAs` and :class:`ArrayOf`) are also handled by the auto generated
mapping process, provided that a mapping has been defined previously for the Resource types that these relations refer
to. There is one special case however, this is where Resource types match; in this situation the
:class:`odin.mapping.helpers.NoOpMapper` is used to transparently copy the items.


Applying transformations to data
--------------------------------

Complex data manipulation can be achieved by passing a field value through a mapping function.

The simplest way to apply a transformation action is to use the :py:meth:`map_field` decorator.

Example::

    class AuthorToNewAuthor(odin.Mapping):
        from_obj = Author
        to_obj = NewAuthor

        @odin.map_field
        def title(self, value):
            return value.title()

In this simple example we are specifying a mapping of the title field that ensures that the title value is title case.

But what about if we want to split a field into multiple outputs or combine multiple values into a single field? Not a
problem, transformation actions can accept and return multiple values. These values just need to specified::

    class AuthorToNewAuthor(odin.Mapping):
        from_obj = Author
        to_obj = NewAuthor

        @odin.map_field(from_field='name', to_field=('first_name', 'last_name'))
        def split_author_name(self, value):
            first_name, last_name = value.split(' ', 1)
            return first_name, last_name


Conversely we could combine these fields::

    class AuthorToNewAuthor(odin.Mapping):
        from_obj = Author
        to_obj = NewAuthor

        @odin.map_field(from_field=('first_name', 'last_name'))
        def name(self, first_name, last_name):
            return "%s %s" % (first_name, last_name)

While this example is extremely simplistic it does demonstrate the flexibility of mapping rules. Not also that a value
for the *to_field* is not specified, the mapping decorators will default to using the method name as the to or from
field if it is not specified.

Odin includes several decorators that preform handle different mapping scenarios.

map_field
~~~~~~~~~

Decorate a mapping class method to mark it as a mapping rule.

``from_field``
    The string name or a tuple of names of the field(s) to map from. The function that is being decorated must accept
    the same number of parameters as fields specified.

``to_field``
    The string name or tuple of names of the field(s) to map to. The function that is being decorated must return a
    tuple with the same number of parameters as fields specified.


map_list_field
~~~~~~~~~~~~~~

Decorate a mapping class method to mark it as a mapping rule. This decorator works in much the same way as the basic
*map_field* except rather than treating the response as a set of fields it treats it as a list result. This allows you
to map list of objects.

``from_field``
    The string name or a tuple of names of the field(s) to map from. The function that is being decorated must accept
    the same number of parameters as fields specified.

``to_field``
    The string name of tuple of names of the field(s) to map to. The function that is being decorated must return a
    tuple with the same number of parameters as fields specified.


assign_field
~~~~~~~~~~~~

This is a special decorator that allows you to generate a value that is assigned to the resulting field.

``to_field``
    The string name or tuple of names of the field(s) to map to. The function that is being decorated must return a
    tuple with the same number of parameters as fields specified.


Low level mapping
-----------------

The final way to specify a mapping is by generating the actual mapping rules directly. A basic mapping rule is a three
part tuple that contains the name of the from field (or tuple of multiple source fields) a transform action or None if
there is no transform required and finally the name of the two field (or tuple of multiple destination fields).

.. note:: The number of input parameters and number of parameters returned by the action methods must much the number
    defined in the mapping. A :class:`odin.exceptions.MappingExecutionError` will be raised if an incorrect number of
    parameters is specified.

A list of mapping rules::

    class AuthorToNewAuthor(odin.Mapping):
        from_obj = Author
        to_obj = NewAuthor

        mappings = (
            ('dob', None, 'date_of_birth'),
        )


.. tip:: Use the :py:meth:`define` and :py:meth:`assign` methods to simplify the definition of mappings. They provides
    many sensible defaults.

While the basic mapping only includes and source, action and destination definitions the mappings structure actually
supports three additional boolean parameters. These are **to_list**, **bind** and **skip_if_none**.

``to_list``
~~~~~~~~~~~

The two list option is what the ``map_list_field`` decorator uses to indicate the the returned object is a list value.

``bind``
~~~~~~~~

For use with action methods defined outside the mapping class, if bind is set to ``True`` the mapping instance is
passed to the action method as the first parameter.

``skip_if_none``
~~~~~~~~~~~~~~~~

This flag changes the way that values that are ``None`` are handled. If set to ``True`` if the from value is ``None``
the value will not be supplied to the destination object allowing the destination objects defaulting process to handle
the value.

Mapping Instances
=================

Mapping instances provide various methods to aid in the mapping process.

Initialisation
--------------

The init method accepts a source object and an optional context. The context is a defaults to a :py:meth:`dict` and
allows any value to be stored or supplied to the mapping.

When using the ``apply`` class method to map a list of objects the context is used to track the index count.

``convert``
-----------

Method that starts the mapping process and returns a populated ``to_obj``.

``update``
----------

Update an existing object with fields from the provided by the ``source_obj``.

``diff``
--------

Compare the field values from the ``source_obj`` with a supplied destination and return all the fields that differ.

``loop_idx``
------------

A convenience property gives access to the current loop index when converting a list of objects.

``loop_depth``
--------------

A convenience property that provides the nested loop depth of the current mapping operation.

``in_loop``
-----------

A convenience property that indicates if the current mapping operation is in a loop.


Mapping Factories
=================

.. automodule:: odin.mapping

When mapping between two objects that are similar eg between a Django model and a resource, or between versions of
resources.

    .. autofunction:: mapping_factory

There is also the simpler method when only a forward mapping is desired.

    .. autofunction:: forward_mapping_factory
