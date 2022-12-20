"""Type aliases for string formatted types."""
from typing import Callable, Union, Any, Sequence, Tuple

__all__ = (
    "Email",
    "IPv4",
    "IPv6",
    "IPv46",
    "Url",
    "Validator",
    "Choices",
)

Validator = Callable[[Any], None]
Choices = Union[
    Sequence[Any],
    Sequence[Tuple[str, Any]],
    Sequence[Tuple[str, Any, str]],
]


class Email(str):
    """Alias for use defining email entries."""

    __slots__ = ()


class IPv4(str):
    """Alias for use defining IPv4 entries."""

    __slots__ = ()


class IPv6(str):
    """Alias for use defining IPv6 entries."""

    __slots__ = ()


class IPv46(str):
    """Alias for use defining IPv4 or IPv6 entries."""

    __slots__ = ()


class Url(str):
    """Alias for use defining URL entries."""

    __slots__ = ()
