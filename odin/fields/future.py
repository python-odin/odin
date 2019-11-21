from __future__ import absolute_import

from typing import TypeVar, Optional, Any  # noqa

from odin.exceptions import ValidationError
from . import Field
from enum import Enum

__all__ = ("EnumField", )


ET = TypeVar('ET', Enum, Enum)


class EnumField(Field):
    """
    Field for handling Python enums.

    This field requires Python >= 3.4 or the enum34 package.

    """
    def __init__(self, enum, **options):
        # type: (ET, **Any) -> None
        options['choices'] = None
        super(EnumField, self).__init__(**options)
        self.enum = enum

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
