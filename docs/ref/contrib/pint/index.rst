#############################
Physical Quantities with Pint
#############################

Additional resources fields that include units.

.. note::

    This contrib module depends on the `Pint units library <http://pint.readthedocs.org/>`_ this can be installed with::

        pip install pint


Fields
******

.. _field-pint_field:

ArrowField
===========

``class ArrowField([assume_local: bool = False, **options])``

An amount.

ArrowField has one extra argument:

:py:attr:`ArrowField.assume_local`
    Customise how naive (datetime values with no timezone) are handled and also how dates are decoded. If
    ``assume_local`` is True naive dates are assumed to represent the current system timezone.
