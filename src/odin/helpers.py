"""
Helpers
~~~~~~~

A collection of useful convenience methods.
"""

from collections import defaultdict

from odin import BaseField
from odin.exceptions import NON_FIELD_ERRORS, ValidationError

__all__ = ("ValidationErrorCollection",)


class ValidationErrorCollection:
    """Helper collection for collecting validation error messages and generating or raising an exception.

    Usage:

    .. code-block:: python

        errors = ValidationErrorCollection()
        ... # Perform validation
        errors.add_message("name", "Value is required")

        if errors:
            raise errors.validation_error()

    """

    def __init__(self):
        """Initialise collection."""
        self.error_messages = defaultdict[str, list[str]](list)

    def __bool__(self):
        return bool(self.messages)

    @property
    def messages(self) -> dict[str, list[str]]:
        """Filtered messages that strips out empty messages."""
        return {
            field_name: messages
            for field_name, messages in self.error_messages.items()
            if messages
        }

    def add_message(self, field: str | BaseField, *messages):
        """Append validation error message(s)."""
        field_name = field if isinstance(field, str) else field.attname
        self.error_messages[field_name].extend(messages)

    def add_resource_message(self, *messages):
        """Append resource level validation error message(s)."""
        self.error_messages[NON_FIELD_ERRORS].extend(messages)

    def raise_if_defined(self):
        """Raise an exception if any are defined."""
        if self:
            raise self.validation_error()

    def validation_error(self) -> ValidationError:
        """Generate an exception based on the validation messages added."""
        return ValidationError(self.messages)
