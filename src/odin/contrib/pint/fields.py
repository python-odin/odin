# -*- coding: utf-8 -*-
from odin import exceptions
from odin.contrib.pint import units
from odin.fields import Field
from odin.validators import EMPTY_VALUES


__all__ = ('FloatQField',)


class FloatQField(Field):
    default_error_messages = {
        'invalid': "'%s' value must be a float.",
        'invalid-unit': "'%s' value must be a %s quantity.",
    }

    def __init__(self, units_, **kwargs):
        super(FloatQField, self).__init__(**kwargs)

        # Ensure we have valid units
        if units_ is None:
            raise ValueError("Units cannot be None")
        #if not units_ in units.registry:
        #    raise ValueError("Units object is not a member of `odin.units.registry`. Any custom units must be "
        #                     "registered with Odin's unit registry.")
        self.units = units_

    def to_python(self, value):
        if value in EMPTY_VALUES:
            return None
        if isinstance(value, tuple):
            pass
        if isinstance(value, units.registry.Quantity):
            if value.units != self.units:
                msg = self.error_messages['invalid-unit'] % (value, self.units.units)
                raise exceptions.ValidationError(msg)
            return value

        try:
            return float(value)
        except ValueError:
            msg = self.error_messages['invalid'] % value
            raise exceptions.ValidationError(msg)

    def to_string(self, value):
        pass
