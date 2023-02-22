#####
Arrow
#####

Better dates & times for Python

.. note::

    This contrib module depends on the `Arrow <https://arrow.readthedocs.io/en/latest/>`_ library::

        pip install arrow

Fields
******

.. _field-arrow_field:

ArrowField
===========

``class ArrowField([assume_local: bool = False, **options])``

An amount.

ArrowField has one extra argument:

:py:attr:`ArrowField.assume_local`
    Customise how naive (datetime values with no timezone) are handled and also how dates are decoded. If
    ``assume_local`` is True naive dates are assumed to represent the current system timezone.
