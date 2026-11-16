# This file is largely inspired by the Django project validators.
import contextlib
import ipaddress
import re
from collections.abc import Callable, Collection
from typing import Any, Final, TypeVar, overload

from odin import exceptions

__all__ = (
    "EMPTY_VALUES",
    "BaseValidator",
    "BetweenValidator",
    "EmailValidator",
    "IPv4Address",
    "LengthValidator",
    "MaxLengthValidator",
    "MaxValueValidator",
    "MinLengthValidator",
    "MinValueValidator",
    "RegexValidator",
    "SimpleValidator",
    "URLValidator",
    "simple_validator",
    "validate_email_address",
    "validate_ipv4_address",
    "validate_ipv46_address",
    "validate_ipv6_address",
    "validate_url",
)

EMPTY_VALUES: Final = (None, "", [], (), {})
MAX_EMAIL_LENGTH: Final = 254
MAX_USER_LENGTH: Final = 64
MAX_DOMAIN_LENGTH: Final = 255


class RegexValidator:
    """Validate that input matches (or does not match) a regular expression."""

    regex: re.Pattern | str = r""
    message: str = "Enter a valid value."
    code: str = "invalid"
    description: str | None = None
    inverse_match: bool = False

    def __init__(
        self,
        regex: str | re.Pattern | None = None,
        message: str | None = None,
        code: str | None = None,
        description: str | None = None,
        inverse_match: bool | None = None,
    ):
        if regex is not None:
            self.regex = regex
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code
        if description is not None:
            self.description = description
        if inverse_match is not None:
            self.inverse_match = inverse_match

        # Compile the regex if it was not passed pre-compiled.
        if isinstance(self.regex, str):
            self.regex = re.compile(self.regex)

    def __call__(self, value: Any):
        """Validate that the input matches (or does not match) the regular expression."""
        if not isinstance(value, str):
            raise exceptions.ValidationError(self.message, code=self.code)

        matched = bool(self.regex.search(value))
        if matched == self.inverse_match:
            raise exceptions.ValidationError(self.message, code=self.code)

    def __str__(self) -> str:
        """Generate str (used by sphinx for documentation)."""
        pattern = getattr(self.regex, "pattern", str(self.regex))
        return (self.description or "{type_name}({pattern})").format(
            type_name=type(self).__name__, pattern=pattern
        )


class URLValidator(RegexValidator):
    """Validate a URL."""

    regex = re.compile(
        r"^(?:http|ftp)s?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|"  # ...or ipv4
        r"\[?[A-F0-9]*:[A-F0-9:]+]?)"  # ...or ipv6
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    message = "Enter a valid URL value."
    description = "Value is a valid URL."


validate_url = URLValidator()


class BaseValidator:
    message: str = "Ensure this value is %(limit_value)s (it is %(show_value)s)."
    code: str = "limit_value"
    description: str = "Value is a {limit_value}."

    __slots__ = ("limit_value",)

    def __init__(self, limit_value: Any):
        self.limit_value = limit_value

    def __call__(self, value: Any):
        cleaned = self.clean(value)
        if self.compare(cleaned, self.limit_value):
            params = {"limit_value": self.limit_value, "show_value": cleaned}
            raise exceptions.ValidationError(
                self.message % params, code=self.code, params=params
            )

    def __str__(self) -> str:
        """Generate str (used by sphinx for documentation)."""
        return self.description.format(
            type_name=type(self).__name__, limit_value=self.limit_value
        )

    def compare(self, a: Any, b: Any) -> bool:
        return a is not b

    def clean(self, value: Any) -> Any:
        return value


class MaxValueValidator(BaseValidator):
    """Validate value is less than or equal to a max value."""

    __slots__ = ()
    message = "Ensure this value is less than or equal to %(limit_value)s."
    code = "max_value"
    description = "Value is less than or equal to {limit_value}."

    def compare(self, a: Any, b: Any) -> bool:
        return a > b


class MinValueValidator(BaseValidator):
    """Validate value is greater than or equal to a min value."""

    __slots__ = ()
    message = "Ensure this value is greater than or equal to %(limit_value)s."
    code = "min_value"
    description = "Value is greater than or equal to {limit_value}."

    def compare(self, a: Any, b: Any) -> bool:
        return a < b


class BetweenValidator(BaseValidator):
    """Validate value is between a min and max value (inclusive)."""

    __slots__ = ("min_value", "max_value")
    message = "Ensure this value is between %(min_value)s and %(max_value)s (it is %(show_value)s)."
    code = "between_values"
    description = "Value is between {min_value} and {max_value}."

    def __init__(self, min_value: Any, max_value: Any):
        self.min_value = min_value
        self.max_value = max_value

    def __call__(self, value: Any):
        cleaned = self.clean(value)
        if cleaned < self.min_value or cleaned > self.max_value:
            params = {
                "min_value": self.min_value,
                "max_value": self.max_value,
                "show_value": cleaned,
            }
            raise exceptions.ValidationError(
                self.message % params, code=self.code, params=params
            )

    def __str__(self) -> str:
        return self.description.format(
            type_name=type(self).__name__,
            min_value=self.min_value,
            max_value=self.max_value,
        )


class LengthValidator(BaseValidator):
    """Validate value has an exact length."""

    __slots__ = ()
    message = (
        "Ensure this value's length is exactly %(limit_value)d (it has %(show_value)d)."
    )
    code = "length"
    description = "Value's length is {limit_value}."

    def compare(self, a: Any, b: Any) -> bool:
        return a != b

    def clean(self, value: Any) -> int:
        return len(value)


class MaxLengthValidator(LengthValidator):
    """Validate value length is at most limit."""

    __slots__ = ()
    message = (
        "Ensure this value's length is at most %(limit_value)d (it has %(show_value)d)."
    )
    code = "max_length"
    description = "Value's length is at most {limit_value}."

    def compare(self, a: Any, b: Any) -> bool:
        return a > b


class MinLengthValidator(LengthValidator):
    """Validate value length is at least limit."""

    __slots__ = ()
    message = "Ensure this value's length is at least %(limit_value)d (it has %(show_value)d)."
    code = "min_length"
    description = "Value's length is at least {limit_value}."

    def compare(self, a: Any, b: Any) -> bool:
        return a < b


class SimpleValidator:
    """Wrapper around a callable to provide simple validation."""

    __slots__ = ("assertion", "message", "code", "description")

    def __init__(
        self,
        assertion: Callable[[Any], bool],
        message: str,
        code: str = "invalid",
        description: str | None = None,
    ):
        self.assertion = assertion
        self.message = message
        self.code = code
        self.description = description

    def __call__(self, value: Any):
        if not self.assertion(value):
            params = {"show_value": value}
            raise exceptions.ValidationError(
                self.message % params
                if "%(show_value)s" in self.message
                else self.message,
                code=self.code,
                params=params,
            )

    def __str__(self) -> str:
        """Generate str (used by sphinx for documentation)."""
        return (
            self.description
            or (self.assertion.__doc__ or self.assertion.__name__).strip()
        )


_A = TypeVar("_A", bound=Callable[[Any], bool])


@overload
def simple_validator(
    assertion: _A,
    *,
    message: str = "The supplied value is invalid",
    code: str = "invalid",
    description: str | None = None,
) -> SimpleValidator: ...


@overload
def simple_validator(
    assertion: None = None,
    *,
    message: str = "The supplied value is invalid",
    code: str = "invalid",
    description: str | None = None,
) -> Callable[[_A], SimpleValidator]: ...


def simple_validator(
    assertion: _A | None = None,
    *,
    message: str = "The supplied value is invalid",
    code: str = "invalid",
    description: str | None = None,
) -> SimpleValidator | Callable[[_A], SimpleValidator]:
    """Create a simple validator.

    :param assertion: A validation exception will be raised if this check returns a non-True value.
    :param message: Message to raised in Validation exception if validation fails.
    :param code: Code to included in Validation exception. This can be used to customise the message at the resource
        level.
    :param description: Optional description to provide information to sphinx for documentation

    Usage::

        >>> none_validator = simple_validator(lambda x: x is not None, message="This value cannot be none")

    This can also be used as a decorator::

        @simple_validator(message="This value cannot be none")
        def none_validator(v):
            return v is not None
    """

    def inner(func: _A) -> SimpleValidator:
        return SimpleValidator(func, message, code, description)

    if assertion is not None:
        return inner(assertion)
    return inner


class IPv4Address:
    """Validate an IPv4 address."""

    message = "Enter a valid IPv4 address."
    code = "invalid"
    description = "Value is an IPv4 Address."

    def __init__(
        self,
        message: str | None = None,
        code: str | None = None,
        description: str | None = None,
    ):
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code
        if description is not None:
            self.description = description

    def __call__(self, value: Any):
        try:
            ipaddress.IPv4Address(value)
        except (ValueError, TypeError):
            raise exceptions.ValidationError(self.message, code=self.code) from None

    def __str__(self) -> str:
        return self.description


validate_ipv4_address = IPv4Address()


def validate_ipv6_address(value: Any):
    """Value is a valid IPv6 Address."""
    try:
        ipaddress.IPv6Address(value)
    except (ValueError, TypeError):
        raise exceptions.ValidationError(
            "Enter a valid IPv6 address.", code="invalid"
        ) from None


def validate_ipv46_address(value: Any):
    """Value is either a valid IPv4 or IPv6 address."""
    try:
        ipaddress.ip_address(value)
    except (ValueError, TypeError):
        raise exceptions.ValidationError(
            "Enter a valid IPv4 or IPv6 address.", code="invalid"
        ) from None


class EmailValidator:
    """Validate is a valid email address format."""

    message = "Enter a valid email address."
    code = "invalid"
    user_regex = re.compile(
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*\Z"  # dot-atom
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"\Z)',  # quoted-string
        re.IGNORECASE,
    )
    domain_regex = re.compile(
        # max length for domain name labels is 63 characters per RFC 1034
        r"((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+)(?:[A-Z0-9-]{2,63}(?<!-))\Z",
        re.IGNORECASE,
    )
    literal_regex = re.compile(
        # literal form, ipv4 or ipv6 address (SMTP 4.1.3)
        r"\[([A-Fa-f0-9:.]+)\]\Z",
        re.IGNORECASE,
    )
    domain_whitelist: frozenset[str] = frozenset({"localhost"})

    def __init__(
        self,
        message: str | None = None,
        code: str | None = None,
        whitelist: Collection[str] | None = None,
    ):
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code
        if whitelist is not None:
            self.domain_whitelist = frozenset(whitelist)

    def __str__(self) -> str:
        """Generate str (used by sphinx for documentation)."""
        return "Value is a valid Email address."

    def __call__(self, value: Any):
        if (
            not value
            or not isinstance(value, str)
            or "@" not in value
            or len(value) > MAX_EMAIL_LENGTH
        ):
            raise exceptions.ValidationError(self.message, code=self.code)

        user_part, domain_part = value.rsplit("@", 1)

        if len(user_part) > MAX_USER_LENGTH or not self.user_regex.match(user_part):
            raise exceptions.ValidationError(self.message, code=self.code)

        if domain_part in self.domain_whitelist:
            return

        if not self.validate_domain_part(domain_part):
            # Try for possible IDN domain-part
            with contextlib.suppress(UnicodeError):
                domain_part = domain_part.encode("idna").decode("ascii")
                if self.validate_domain_part(domain_part):
                    return
            raise exceptions.ValidationError(self.message, code=self.code)

    def validate_domain_part(self, domain_part: str) -> bool:
        if len(domain_part) <= MAX_DOMAIN_LENGTH and self.domain_regex.match(
            domain_part
        ):
            return True

        literal_match = self.literal_regex.match(domain_part)
        if literal_match:
            ip_addr_str = literal_match.group(1)
            try:
                validate_ipv46_address(ip_addr_str)
                return True
            except exceptions.ValidationError:
                return False
        return False


validate_email_address = EmailValidator()
