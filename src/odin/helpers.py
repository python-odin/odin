"""
Helpers
~~~~~~~

A collection of useful convenience methods.
"""

from collections import defaultdict
from collections.abc import Iterator, Mapping
from typing import TYPE_CHECKING, Any

from odin.exceptions import NON_FIELD_ERRORS, ValidationError

if TYPE_CHECKING:
    from odin.fields.base import BaseField

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
        self.error_messages: dict[str, list[str]] = defaultdict(list)

    def __bool__(self) -> bool:
        return any(bool(msgs) for msgs in self.error_messages.values())

    def __len__(self) -> int:
        return len(self.messages)

    def __contains__(self, field: "str | BaseField") -> bool:
        field_name = field if isinstance(field, str) else field.attname
        return bool(self.error_messages.get(field_name))

    def __getitem__(self, field: "str | BaseField") -> list[str]:
        field_name = field if isinstance(field, str) else field.attname
        return self.error_messages[field_name]

    def __iter__(self) -> Iterator[str]:
        return iter(self.messages)

    def __enter__(self) -> "ValidationErrorCollection":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.raise_if_defined()

    @property
    def messages(self) -> dict[str, list[str]]:
        """Filtered messages that strips out empty messages."""
        return {
            field_name: messages
            for field_name, messages in self.error_messages.items()
            if messages
        }

    @property
    def message_count(self) -> int:
        """Total number of messages across all fields."""
        return sum(len(messages) for messages in self.error_messages.values())

    def add_message(self, field: "str | BaseField | None", *messages: str):
        """Append validation error message(s)."""
        if not messages:
            return
        if field is None:
            field_name = NON_FIELD_ERRORS
        elif isinstance(field, str):
            field_name = field
        else:
            field_name = field.attname
        self.error_messages[field_name].extend(messages)

    def add_resource_message(self, *messages: str):
        """Append resource level validation error message(s)."""
        if messages:
            self.error_messages[NON_FIELD_ERRORS].extend(messages)

    def add_error(self, field: "str | BaseField | None", error: ValidationError):
        """Ingest messages from an existing ValidationError."""
        if hasattr(error, "message_dict"):
            for f_name, msgs in error.message_dict.items():
                self.add_message(f_name, *msgs)
        elif hasattr(error, "messages"):
            self.add_message(field, *error.messages)

    def clear(self):
        """Clear all collected error messages."""
        self.error_messages.clear()

    def raise_if_defined(self):
        """Raise an exception if any are defined."""
        if self:
            raise self.validation_error()

    def validation_error(self) -> ValidationError:
        """Generate an exception based on the validation messages added."""
        return ValidationError(self.messages)
