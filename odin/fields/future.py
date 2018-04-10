from __future__ import absolute_import

from typing import TypeVar, Type, Optional, Any  # noqa

from odin.exceptions import ValidationError
from . import Field

try:
    from enum import Enum, EnumMeta
except ImportError:
    Enum = None

_all_fields = []

if Enum:
    _all_fields.append('EnumField')

    ET = TypeVar('ET', Enum, Enum)

    class EnumField(Field):
        """
        Field for handling Python enums.

        This field requires Python >= 3.5 or the enum35 package.

        """
        def __init__(self, enum, **options):
            # type: (Type[ET]) -> None
            options['choices'] = None
            super(EnumField, self).__init__(**options)
            self.enum = enum  # type: Type[Enum]

        def to_python(self, value):
            # type: (Any) -> Optional[ET]
            if value is None:
                return

            # Is the value in the enum
            if value in self.enum:
                return value

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
