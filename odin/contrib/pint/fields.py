# -*- coding: utf-8 -*-
from pint.unit import DimensionalityError
import six
from odin import exceptions
from odin.contrib.pint.units import registry
from odin.fields import Field
from odin.validators import EMPTY_VALUES

__all__ = ('FloatQField',)


class FloatQField(Field):
    default_error_messages = {
        'invalid': "'%s' value must be a float.",
    }

    def __init__(self, units, **kwargs):
        super(FloatQField, self).__init__(**kwargs)

        # Ensure we have valid units
        if units is None:
            raise ValueError("Units cannot be None")
        if isinstance(units, six.string_types):
            units = registry[units]
        #if not units_ in units.registry:
        #    raise ValueError("Units object is not a member of `odin.units.registry`. Any custom units must be "
        #                     "registered with Odin's unit registry.")
        self.units = units

    def to_python(self, value):
        if value in EMPTY_VALUES:
            return None
        if not isinstance(value, registry.Quantity):
            if isinstance(value, tuple) and len(value) == 2:
                magnitude, units = value
            else:
                magnitude, units = value, self.units
            if isinstance(units, six.string_types):
                units = registry[units]
            try:
                value = float(magnitude) * units
            except ValueError:
                msg = self.error_messages['invalid'] % value
                raise exceptions.ValidationError(msg)
        try:
            return value.to(self.units)
        except DimensionalityError as de:
            raise exceptions.ValidationError(de)
