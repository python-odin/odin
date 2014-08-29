# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
from odin import exceptions
from odin.fields import Field
from odin.validators import EMPTY_VALUES
from .datatypes import Amount

__all__ = ('AmountField', )


class AmountField(Field):
    """
    Field that contains a monetary amount (with an optional currency).
    """
    default_error_messages = {
        'invalid': "'%s' value must be a (amount, currency).",
    }

    def to_python(self, value):
        if value in EMPTY_VALUES:
            return
        try:
            return Amount(value)
        except (ValueError, TypeError):
            msg = self.error_messages['invalid'] % value
            raise exceptions.ValidationError(msg)
