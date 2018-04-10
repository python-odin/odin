from __future__ import absolute_import

from typing import TypeVar, Type, Optional, Any  # noqa

from odin.exceptions import ValidationError
from . import Field

try:
    from enum import Enum
except ImportError:
    Enum = None

_all_fields = []

if Enum:
    _all_fields.append('EnumField')

    ET = TypeVar('ET', Enum, Enum)

    class EnumField(Field):
        """
        Field for handling Python enums.

        This field requires Python >= 3.4 or the enum34 package.

        """
        def __init__(self, enum, **options):
            # type: (Type[Enum]) -> None
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
                raise ValidationError(self.error_messages['invalid_choice'] % value)

        def prepare(self, value):
            # type: (Optional[Enum]) -> str
            if value in self.enum:
                return value.value


__all__ = tuple(_all_fields)
