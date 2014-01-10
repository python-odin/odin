########################
Resource field reference
########################

This section contains all the details of the resource fields built into JSRN.

Field options
*************

The following arguments are available to all field types. All are optional.


.. _field-option-verbose_name:

verbose_name
============
``Field.verbose_name``

A human-readable name for the field. If the verbose name isn’t given, JSRN will automatically create it using the
field’s attribute name, converting underscores to spaces.


.. _field-option-verbose_name_plural:

verbose_name_plural
===================
``Field.verbose_name_plural``

A human-readable plural name for the field. If the verbose name plural isn’t given, JSRN will automatically create it
using the verbose name and appending an s.


.. _field-option-name:

name
====
``Field.name``

Name of the field as it appears in the JSON document. If the name isn't given, JSRN will use the field's attribute name.


.. _field-option-required:

required
========
``Field.required``

If ``True`` JSRN will ensure that this field has been specified in a JSON document and raise a validation error if the
field is missing.

If ``False`` JSRN will ignore the field and a default value (or ``None`` if a default is not supplied) will be place. In
addition both the :ref:`field-option-blank` and :ref:`field-option-null` will be assumed to be ``True``.


.. _field-option-blank:

blank
=====
``Field.blank``

If ``True``, the field is allowed to be blank. Default is ``False``.

Note that this is different than ``null``. If a field has ``blank=True``, validation will allow entry of an empty value.
If a field has ``blank=False``, the field will be required.

If ``False`` JSRN will raise a validation error if a value is blank, a blank value is a empty string or list.


.. _field-option-null:

null
====
``Field.null``

If ``True`` JSRN will raise a validation error if a value is ``null``. Default is ``False``.


.. _field-option-default:

default
=======
``Field.default``

The default value for the field. This can be a value or a callable object. If callable it will be called every time a
new object is created.


.. _field-option-choices:

choices
=======
``Field.choices``

An iterable (e.g., a list or tuple) of 2-tuples to use as choices for this field. If this is given, the choices are used
to validate entries, it is also used in documentation generation.

A choices list looks like this:
::

    GENRE_CHOICES = (
        ('sci-fi', 'Science Fiction'),
        ('fantasy', 'Fantasy'),
        ('others', 'Others'),
    )

The first element in each tuple is the value that will be used to validate, the second element is used for
documentation. For example:
::

    import jsrn

    class Book(jsrn.Resource):
        GENRE_CHOICES = (
            ('sci-fi', 'Science Fiction'),
            ('fantasy', 'Fantasy'),
            ('others', 'Others'),
        )
        title = jsrn.StringField()
        genre = jsrn.StringField(choices=GENRE_CHOICES)
    >>> b = Book(title="Consider Phlebas", genre="sci-fi")
    >>> b.genre
    'sci-fi'
    >>> b.get_genre_display()
    'Science Fiction'


.. _field-option-help_text:

help_text
=========
``Field.help_text``

Extra “help” text to be displayed generated documentation. It’s also useful for inline documentation even if
documentation is not generated.


Base JSON fields
****************

Fields that map one-to-one with JSON data types

.. _field-string_field:

StringField
===========
``class StringField([max_length=None, **options])``
A string field, for small- to large-sized strings.

StringField has one extra argument:

``StringField.max_length``
    The maximum length (in characters) of the field. The ``max_length`` value is enforced JSRN’s validation.

.. _field-integer_field:

IntegerField
============
``class IntegerField([min_value=None, max_value=None, **options])``

An integer.

IntegerField has two extra arguments:

``IntegerField.min_value``
    The minimum value of the field. The ``min_value`` value is enforced JSRN’s validation.

``IntegerField.max_value``
    The maximum value of the field. The ``max_value`` value is enforced JSRN’s validation.


.. _field-float_field:

FloatField
==========
``class FloatField([**options])``

A floating-point number represented in Python by a *float* instance.

FloatField has two extra arguments:

``FloatField.min_value``
    The minimum value of the field. The ``min_value`` value is enforced JSRN’s validation.

``FloatField.max_value``
    The maximum value of the field. The ``max_value`` value is enforced JSRN’s validation.

.. _field-boolean_field:

BooleanField
============
``class BooleanField([**options])``

A true/false field.

.. _field-date_time_field:

DateTimeField
=============
``class DateTimeField([**options])``

A string encoded date time field, that represents a JavaScript Date. The format of the string is that defined by ECMA
international standard ECMA-262 section 15.9.1.15. Note that the standard encodes all dates as UTC.

DateTimeField has an extra argument:

``DateTimeField.assume_local``
    This adjusts the behaviour of how naive date times (date time objects with no timezone) are handled. By default
    assume_local is True, in this state naive date times are assumed to be in the current system timezone so a
    conversion is applied when encoding to be in UTC. Similarly on decoding a datetime string the output datetime will
    be converted to the current system timezone.

.. _field-array_field:

ArrayField
==========
``class ArrayField([**options])``

An array structure represented in Python by a *list* instance.

.. note: The items in the array are not defined.

.. _field-typed_array_field:

TypedArrayField
===============
``class TypedArrayField(field, [**options])``

An array structure represented in Python by a *list* instance accepts an additional parameter of another field type that
each entry in the array is validated against.

``TypedArrayField.field``
    The field that is used to validate each entry in the array.

.. _field-object_field:

ObjectField
===========
``class ObjectField([**options])``

An object structure represented in Python by a *dict* instance.

.. note: The object values in the object are not defined.

.. _field-composite_fields:

Composite fields
****************

JSRN also defines a set of fields that allow for composition.


.. _field-objectas_field:

ObjectAs field
==============
``class ObjectAs(of[, **options])``

A child object. Requires a positional argument: the class that represents the child resource.

.. note: A default `dict` is automatically assigned.

JSON Representation
-------------------

This field represents a child JSON object.

Example, the *publisher* object:
::

    {
        "title": "Consider Phlebas",
        "publisher": {
            "name": "Macmillan"
        }
    }


.. _field-arrayof_field:

ArrayOf field
=============
``class ArrayOf(of[, **options])``

A child list. Requires a positional argument: the class that represents a list of resources.

.. note: A default `list` is automatically assigned.

JSON Representation
-------------------

This field represents a child JSON array.

Example, the *authors* array:
::

    {
        "title": "Consider Phlebas",
        "authors": [
            {
                "$": "Author",
                "name": "Iain M. Banks"
            }
        ]
    }


