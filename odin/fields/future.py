from __future__ import absolute_import

from enum import Enum, IntEnum
from typing import TypeVar, Optional, Any  # noqa

from odin.exceptions import ValidationError
from odin.utils import lazy_property
from . import Field

__all__ = ("EnumField", )


ET = TypeVar('ET', Enum, Enum)


class EnumField(Field):
    """
    Field for handling Python enums.
    """

    data_type_name = "Enum"

    def __init__(self, enum, **options):
        # type: (ET, **Any) -> None
        
        # Generate choices if not defined)
        if "choices" not in options:
            options["choices"] = tuple((e, e.name) for e in enum)

        super(EnumField, self).__init__(**options)
        self.enum = enum

        if isinstance(enum, IntEnum):
            self.data_type_name = "Integer Enum"

    @property
    def choice_doc_text(self):
        """
        Choices converted for documentation purposes.
        """
        return tuple((v.value, n) for v, n in self.choices)

    def to_python(self, value):
        # type: (Any) -> Optional[ET]
        if value is None:
            return

        # Attempt to convert
        try:
            return self.enum(value)
        except ValueError:
            # If value is an empty string return None
            # Do this check here to support enums that define an option using
            # an empty string.
            if value is "":
                return
            raise ValidationError(self.error_messages['invalid_choice'] % value)

    def prepare(self, value):
        # type: (Optional[ET]) -> Any
        if value in self.enum:
            return value.value
