###################
Annotated Resources
###################

A resource is a collection of fields and associated meta data that is used to validate data within the fields.

The basics:
 * Each annotated resource is a Python class that subclasses :class:`odin.AnnotatedResource`.
 * Each field attribute of the resource is defined type attributes.
 * Additional field options can be provided using :class:`odin.Options`.

Quick example
=============

This example resource defines a ``Book``, which has a ``title``, ``genre`` and ``num_pages``:

.. code-block:: python

    import odin

    class Book(odin.AnnotatedResource):
        title: str
        genre: str
        num_pages: int
        rrp: float = 24.5

``title``, ``genre``, ``num_pages`` and ``rrp`` are fields. Each field is specified as a class attribute, the ``rrp``
field has a default value of ``24.5``.

The above ``Book`` resource would create a JSON object like this:

.. code-block:: json

    {
        "$": "resources.Book",
        "title": "Consider Phlebas",
        "genre": "Space Opera",
        "num_pages": 471,
        "rrp": 24.5
    }

Some technical notes:
 * The ``$`` field is a special field that defines the type of ``AnnotatedResource``.
 * The name of the resource, ``resources.Book``, is automatically derived from some resource metadata but can be
   overridden.

Fields
======

The most important part of a resource – and the only required part of a resource – is the list of fields it defines.
Fields are specified by attributes. Be careful not to choose field names that conflict with the resources API like
``clean``.

Example:

.. code-block:: python

    class Author(odin.AnnotatedResource):
        name: str

    class Book(odin.AnnotatedResource):
        title: str
        authors: List[Author]
        genre: str
        num_pages: int
        rrp: float = 24.5

Field types
-----------

Each field in your annotated resource must include a type annotation that odin uses to determine the appropriate field
type.


Supported Annotations
---------------------

All basic types of field are supported by Odin, ``str``, ``bool``, ``int``, ``float``, ``dict``, ``list``,
``datetime.datetime``, ``datatime.date``, ``datetime.time``, ``uuid.UUID`` and ``pathlib.Path``. These all map to the
appropriate odin field along with any options.

Odin also includes a number of builtin type aliases for commonly used field types via the ``odin.types`` alias
``odin.types.Email``, ``odin.types.IPv4``, ``odin.types.IPv6``, ``odin.types.IPv46`` and ``odin.types.Url``.

Enum types are supported by simply specifying an enum type.

Composite fields are supported using generic type hints, the ``List``/``Sequence`` and ``Mapping``/``Dict`` type
specifiers will map to the appropriate fields based on the arguments provided.

Finally use of the ``Optional`` typing alias is used to set the ``null`` field option.


Field options
-------------

Options are provided to the appropriate field using the ``odin.Options`` class. This will be identified by Odin
with the options passed to the resolved field type.

An example:

.. code-block:: python

    class Book(odin.AnnotatedResource):
        title: str = odin.Options(min_length=1)

The first value of the ``Options`` class is the default value, the ``Options`` object cna be left out if only a default
value needs to be provided.

To defined a completely custom field type use the ``field_type`` option, to pass a field instance that will be used for
the field.


Resource inheritance
====================

Resource inheritance in Odin works almost identically to the way normal class inheritance works in Python. The only
decision you have to make is whether you want the parent resources to be resources in their own right, or if the parents
are just holders of common information that will only be visible through the child resources.

.. _resources-abstract:

Abstract base classes
---------------------

Abstract base classes are useful when you want to put some common information into a number of other resources. You
write your base class and put abstract=True in the Meta class. This resource will then not be able to created from a
JSON document. Instead, when it is used as a base class for other resources, its fields will be added to those of the
child class.

An example::

    class CommonBook(odin.AnnotatedResource, abstract=True):
        title: str


    class PictureBook(CommonBook):
        photographer: str

The PictureBook resource will have two fields: title and photographer. The CommonBook resource cannot be used as a
normal resource, since it is an abstract base class.
