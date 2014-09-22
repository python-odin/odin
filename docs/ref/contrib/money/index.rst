#########################
Currency and Money Values
#########################

Fields and data types that handle money values.

:todo: This section is in progress

Datatypes
*********

Amount
======

Combines an value and a Currency to represent a monetary amount.


Currency
========

Defines a currency and maintains metadata about the currency.


Fields
******

.. _field-amount_field:

AmountField
===========

``class AmountField([allowed_currencies=None, min_value=None, max_value=None, **options])``

An amount.

AmountField has three extra arguments:

:py:attr:`AmountField.allowed_currencies`
    The currencies that can be accepted by this field, value is enforced Odin’s validation. If ``None`` is supplied any
    currency is acceptable.

:py:attr:`AmountField.min_value`
    The minimum amount that can be accepted.

:py:attr:`AmountField.max_value`
    The maximum amount that can be accepted.
