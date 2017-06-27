###################
Resources Instances
###################

A resource is a collection of fields and associated meta data that is used to validate data within the fields.

The basics:
 * Each resource is a Python class that subclasses :class:`odin.Resource`.
 * Each field attribute of the resource is defined by a :class:`odin.Field` subclass.

Quick example
=============

This example resource defines a ``Book``, which has a ``title``, ``genre`` and ``num_pages``::

    import odin

    class Book(odin.Resource):
        title = odin.StringField()
        genre = odin.StringField()
        num_pages = odin.IntegerField()

``title``, ``genre`` and ``num_pages`` are fields. Each field is specified as a class attribute.

The above ``Book`` resource would create a JSON object like this::

    {
        "$": "resources.Book",
        "title": "Consider Phlebas",
        "genre": "Space Opera",
        "num_pages": 471
    }

Some technical notes:
 * The ``$`` field is a special field that defines the type of ``Resource``.
 * The name of the resource, ``resources.Book``, is automatically derived from some resource metadata but can be 
   overridden.

Fields
======

The most important part of a resource – and the only required part of a resource – is the list of fields it defines.
Fields are specified by class attributes. Be careful not to choose field names that conflict with the resources API like
``clean``.

Example::

    class Author(odin.Resource):
        name = odin.StringField()

    class Book(odin.Resource):
        title = odin.StringField()
        authors = odin.ArrayOf(Author)
        genre = odin.StringField()
        num_pages = odin.IntegerField()

Field types
-----------

Each field in your resource should be an instance of the appropriate Field class. ODIN uses the field class types to
determine a few things:

* The data type (e.g. ``Integer``, ``String``).
* Validation requirements.


Field options
-------------

Each field takes a certain set of field-specific arguments (documented in the resource field reference).

There’s also a set of common arguments available to all field types. All are optional. They’re fully explained in the
reference, but here’s a quick summary of the most often-used ones:

``null``
    If ``True``, the field is allowed to be null. Default is ``False``.

``default``
    The default value for the field. This can be a value or a callable object. If callable it will be called every time
    a new object is created.

``choices``
    An iterable (e.g., a list or tuple) of 2-tuples to use as choices for this field.

    A choices list looks like this::

        GENRE_CHOICES = (
            ('sci-fi', 'Science Fiction'),
            ('fantasy', 'Fantasy'),
            ('others', 'Others'),
        )

    The first element in each tuple is the value that will be stored field or serialised document, the second element is 
    a display value.

Again, these are just short descriptions of the most common field options.

Verbose field names
-------------------

Each field type, except for ``DictAs`` and ``ArrayOf``, takes an optional first positional argument – a verbose name.
If the verbose name isn’t given, Odin will automatically create it using the field’s attribute name, converting
underscores to spaces.

In this example, the verbose name is "person's first name"::

    first_name = odin.StringField("person's first name")

In this example, the verbose name is "first name"::

    first_name = odin.StringField()

``DictAs`` and ``ArrayOf`` require the first argument to be a resource class, so use the ``verbose_name`` keyword
argument::

    publisher = odin.DictAs(Publisher, verbose_name="the publisher")
    authors = odin.ArrayOf(Author, verbose_name="list of authors")

Resource level validation
-------------------------

Field validation can be customised at the resource level. This is useful as it allows validation of data using a value
from another field for example ensuring a maximum value is greater than a minimum value, or checking that a password
and a check password matches.

This is achieved using by defining a method called ``clean_FIELDNAME`` which accepts a single value argument, Odin will
then use this method during the cleaning process to validate the field. Odin will then use the value that is returned
from the clean method, allowing you to apply any customised formatting. If an issue is found with a value then raise a
:class:`odin.exceptions.ValidationError` and the error returned will be applied to validation results.

Example::

    class Timing(odin.Resource):
        minimum_delay = odin.IntegerField(min_value=0)
        maximum_delay = odin.IntegerField()

        def clean_maximum_delay(self, value):
            if value < self.minimum_delay:
                raise ValidationError('Maximum delay must be greater than the minimum delay value')
            return value

.. important:: Ensure that a return value is provided, if no return value is specified the Python default is
    :const:`None` and this is the value that Odin will use.


Relationships
-------------

To really model more complex documents objects and lists need to be able to be combined, Odin offers ways to define
these structures, :class:`DictAs` and :class:`ArrayOf` fields handle these structures.

DictAs relationships
````````````````````

To define a object-as relationship, use :class:`odin.DictAs`. You use it just like any other Field type by including
it as a class attribute of your resource.

:class:`DictAs` requires a positional argument: the class to which the resource is related.

For example, if a ``Book`` resource has a ``Publisher`` – that is, a single ``Publisher`` publishes a book::

    class Publisher(odin.Resource):
        # ...

    class Book(odin.Resource):
        publisher = odin.DictAs(Publisher)
        # ...

This would produce a JSON document of::

    {
        "$": "resources.Book",
        "title": "Consider Phlebas",
        "publisher": {
            "$": "resources.Publisher",
            "name": "Macmillan"
        }
    }

ArrayOf relationships
`````````````````````

To define a array-of relationship, use ``odin.ArrayOf``. You use it just like any other Field type by including it as a
class attribute of your resource.

``ArrayOf`` requires a positional argument: the class to which the resource is related.

For example, if a ``Book`` resource has a several ``Authors`` – that is, a multiple authors can publish a book::

    class Author(odin.Resource):
        # ...

    class Book(odin.Resource):
        authors = odin.ArrayOf(Author)
        # ...

This would produce a JSON document of::

    {
        "$": "resources.Book",
        "title": "Consider Phlebas",
        "authors": [
            {
                "$": "resources.Author",
                "name": "Iain M. Banks"
            }
        ]
    }


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

    class CommonBook(odin.Resources):
        title = odin.StringField()

        class Meta:
            abstract = True

    class PictureBook(CommonBook):
        photographer = odin.StringField()

The PictureBook resource will have two fields: title and photographer. The CommonBook resource cannot be used as a
normal resource, since it is an abstract base class.

:todo: Add details of how to support multiple object types in a list using Abstract resources
