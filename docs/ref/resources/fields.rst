###############
Field reference
###############

This section contains all the details of the resource fields built into Odin.

.. automodule:: odin.fields


Field options
*************

The following arguments are available to all field types. All are optional.

.. _field-option-verbose_name:

verbose_name
============
:py:attr:`Field.verbose_name`

A human-readable name for the field. If the verbose name isn’t given, Odin will automatically create it using the
field’s attribute name, converting underscores to spaces.

.. _field-option-verbose_name_plural:

verbose_name_plural
===================
:py:attr:`Field.verbose_name_plural`

A human-readable name for the field. If the verbose name isn’t given, Odin will automatically create it using the
field’s attribute name, converting underscores to spaces.

.. _field-option-name:

name
====
:py:attr:`Field.name`

Name of the field as it appears in the exported document. If the name isn't given, Odin will use the field's attribute
name.

.. _field-option-null:

null
====
:py:attr:`Field.null`

If ``True`` Odin will raise a validation error if a value is ``null``. Default is ``False``.

.. _field-option-choices:

choices
=======
:py:attr:`Field.choices`

An iterable (e.g., a list or tuple) of 2-tuples to use as choices for this field. If this is given, the choices are used
to validate entries.

.. note::
    Choices are also used by the :py:mod:`odin.contrib.doc_gen` to generate documentation.

A choices list looks like this::

    GENRE_CHOICES = (
        ('sci-fi', 'Science Fiction'),
        ('fantasy', 'Fantasy'),
        ('others', 'Others'),
    )

The first element in each tuple is the value that will be used to validate, the second element is used for
documentation. For example::

    import Odin

    class Book(Odin.Resource):
        GENRE_CHOICES = (
            ('sci-fi', 'Science Fiction'),
            ('fantasy', 'Fantasy'),
            ('others', 'Others'),
        )
        title = Odin.StringField()
        genre = Odin.StringField(choices=GENRE_CHOICES)
    >>> b = Book(title="Consider Phlebas", genre="sci-fi")
    >>> b.genre
    'sci-fi'

.. _field-option-default:

default
=======
:py:attr:`Field.default`

The default value for the field. This can be a value or a callable object. If callable it will be called every time a
new object is created.

.. _field-option-doc_text:

doc_text (help_text)
====================
:py:attr:`Field.doc_text`

Doc text is used by the :py:mod:`odin.contrib.doc_gen` to generate documentation.

.. note::
    ``help_text`` will be deprecated in a future release in favor of ``doc_text``.

Also useful for inline documentation even if documentation is not generated.

.. _field-option-validators:

validators
==========
:py:attr:`Field.validators`


.. _field-option-error_messages:

error_messages
==============
:py:attr:`Field.error_messages`

.. _field-option-is_attribute:

is_attribute
============
:py:attr:`Field.is_attribute`

.. _field-option-use_default_if_not_provided:

use_default_if_not_provided
===========================
:py:attr:`Field.use_default_if_not_provided`


Standard fields
***************

Simple field types.

.. _field-string_field:

StringField
===========

``class StringField([max_length=None, **options])``

A string.

StringField has one extra argument:

:py:attr:`StringField.max_length`
    The maximum length (in characters) of the field. The ``max_length`` value is enforced Odin’s validation.


.. _field-integer_field:

IntegerField
============
``class IntegerField([min_value=None, max_value=None, **options])``

An integer.

IntegerField has two extra arguments:

:py:attr:`IntegerField.min_value`
    The minimum value of the field. The :py:attr:`min_value` value is enforced Odin’s validation.

:py:attr:`IntegerField.max_value`
    The maximum value of the field. The :py:attr:`max_value` value is enforced Odin’s validation.


.. _field-float_field:

FloatField
==========
``class FloatField([**options])``

A floating-point number represented in Python by a *float* instance.

FloatField has two extra arguments:

:py:attr:`FloatField.min_value`
    The minimum value of the field. The :py:attr:`min_value` value is enforced Odin’s validation.

:py:attr:`FloatField.max_value`
    The maximum value of the field. The :py:attr:`max_value` value is enforced Odin’s validation.

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

:py:attr:`DateTimeField.assume_local`
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

:py:attr:`TypedArrayField.field`
    An instance of an odin field that is used to validate each entry in the array.

.. _field-object_field:

DictField
=========
``class DictField([**options])``

A dictionary.

.. note::
    The object values in the object are not defined.

.. _field-composite_fields:

Composite fields
****************

Odin also defines a set of fields that allow for composition.


.. _field-object_as_field:

DictAs field
============
``class DictAs(of[, **options])``

A child object. Requires a positional argument: the class that represents the child resource.

.. note::
    A default `dict` is automatically assigned.

.. _field-arrayof_field:

ArrayOf field
=============
``class ArrayOf(of[, **options])``

A child list. Requires a positional argument: the class that represents a list of resources.

.. note::
    A default `list` is automatically assigned.