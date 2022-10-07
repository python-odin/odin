from enum import Enum
from typing import TypeVar, Optional, Type

from odin.exceptions import ValidationError
from . import Field

__all__ = ("EnumField",)


ET = TypeVar("ET", Enum, Enum)


class EnumField(Field):
    """
    Field for handling Python enums.
    """

    data_type_name = "Enum"

    def __init__(self, enum: Type[ET], **options):

        # Generate choices structure from choices
        choices = options.pop("choices", None)
        options["choices"] = tuple((e, e.name) for e in choices or enum)

        super().__init__(**options)
        self.enum = enum

    @property
    def choices_doc_text(self):
        """
        Choices converted for documentation purposes.
        """
        return tuple((v.value, n) for v, n in self.choices)

    def to_python(self, value) -> Optional[ET]:
        if value is None:
            return

        # Attempt to convert
        try:
            return self.enum(value)
        except ValueError:
            # If value is an empty string return None
            # Do this check here to support enums that define an option using
            # an empty string.
            if value == "":
                return
            raise ValidationError(self.error_messages["invalid_choice"] % value)

    def prepare(self, value: Optional[ET]):
        if (value is not None) and isinstance(value, self.enum):
            return value.value
