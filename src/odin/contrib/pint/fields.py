from abc import ABC

from pint import errors

from odin import exceptions
from odin.fields import Field
from odin.validators import EMPTY_VALUES

from .units import registry

__all__ = ("FloatField",)


class PintField(Field, ABC):
    """Base class for Pint fields."""

    def __init__(self, units: str, **kwargs):
        super().__init__(**kwargs)

        # Ensure we have valid units
        if units is None:
            raise ValueError("Units cannot be None")
        if isinstance(units, str):
            units = registry[units]
        # if not units_ in units.registry:
        #    raise ValueError("Units object is not a member of `odin.contrib.pint.units.registry`.
        #                      Any custom units must be registered with Odin's unit registry.")
        self.units = units

    def to_quantity(self, value):
        if not isinstance(value, registry.Quantity):
            # Split out units from underlying magnitudes
            if isinstance(value, (tuple, list)) and len(value) == 2:
                raw_value, units = value
            else:
                raw_value, units = value, self.units
            # Extract the units
            if isinstance(units, str):
                units = registry[units]
            # Convert the magnitude and apply units
            value = self.to_magnitude(raw_value) * units

        try:
            return value.to(self.units)
        except errors.DimensionalityError as ex:
            raise exceptions.ValidationError(str(ex)) from None

    def to_magnitude(self, value):
        raise NotImplementedError()


class FloatField(PintField):
    default_error_messages = {
        "invalid": "'%s' value must be a float.",
    }
    data_type_name = "Float"

    def to_magnitude(self, value) -> float:
        """Convert value to a float."""
        try:
            return float(value)

        except ValueError:
            msg = self.error_messages["invalid"] % value
            raise exceptions.ValidationError(msg) from None

    def to_python(self, value):
        """Convert value to a float."""
        if value in EMPTY_VALUES:
            return None
        return self.to_quantity(value)
