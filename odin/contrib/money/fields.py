# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
from odin import exceptions
from odin.fields import ScalarField
from odin.validators import EMPTY_VALUES
from .datatypes import Amount

__all__ = ('AmountField', )


class AmountField(ScalarField):
    """
    Field that contains a monetary amount (with an optional currency).
    """
    default_error_messages = {
        'invalid': "'%s' value must be a (amount, currency).",
        'invalid_currency': "'%s' currency is not supported.",
    }
    data_type_name = "Amount"

    def __init__(self, allowed_currencies=None, **kwargs):
        super(AmountField, self).__init__(**kwargs)
        self.allowed_currencies = allowed_currencies

    def to_python(self, value):
        if value in EMPTY_VALUES:
            return
        if isinstance(value, Amount):
            return value

        try:
            return Amount(value)
        except (ValueError, TypeError):
            msg = self.error_messages['invalid'] % value
            raise exceptions.ValidationError(msg)

    def validate(self, value):
        super(AmountField, self).validate(value)
        if self.allowed_currencies and value not in EMPTY_VALUES:
            if value.currency not in self.allowed_currencies:
                msg = self.error_messages['invalid_currency'] % value.currency
                raise exceptions.ValidationError(msg)

    def prepare(self, value):
        if value in EMPTY_VALUES:
            return
        return float(value), value.currency.code
