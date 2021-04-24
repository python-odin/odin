# -*- coding: utf-8 -*-
from pint.unit import DimensionalityError
import six
from odin import exceptions
from odin.contrib.pint.units import registry
from odin.fields import Field
from odin.validators import EMPTY_VALUES

__all__ = ('FloatField',)


class PintField(Field):
    def __init__(self, units, **kwargs):
        super(PintField, self).__init__(**kwargs)

        # Ensure we have valid units
        if units is None:
            raise ValueError("Units cannot be None")
        if isinstance(units, six.string_types):
            units = registry[units]
        # if not units_ in units.registry:
        #    raise ValueError("Units object is not a member of `odin.units.registry`. Any custom units must be "
        #                     "registered with Odin's unit registry.")
        self.units = units

    def to_quantity(self, value):
        if not isinstance(value, registry.Quantity):
            # Split out units from underlying magnitudes
            if isinstance(value, (tuple, list)) and len(value) == 2:
                raw_value, units = value
            else:
                raw_value, units = value, self.units
            # Extract the units
            if isinstance(units, six.string_types):
                units = registry[units]
            # Convert the magnitude and apply units
            value = self.to_magnitude(raw_value) * units

        try:
            return value.to(self.units)
        except DimensionalityError as de:
            raise exceptions.ValidationError(de)

    def to_magnitude(self, value):
        raise NotImplementedError()


class FloatField(PintField):
    default_error_messages = {
        'invalid': "'%s' value must be a float.",
    }
    data_type_name = "Float"

    def to_magnitude(self, value):
        try:
            return float(value)
        except ValueError:
            msg = self.error_messages['invalid'] % value
            raise exceptions.ValidationError(msg)

    def to_python(self, value):
        if value in EMPTY_VALUES:
            return None
        return self.to_quantity(value)
