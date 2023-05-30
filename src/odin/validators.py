# This file is largely verbatim from the Django project, the wheel works well, no need to re-invent it.
#
# A note: to use validators from the Django project install the baldr package. Baldr is an integration between Odin and
# the Django framework, the integration includes support for handling the Django version of the ValidationError
# exception within Odin.
import re
from typing import Any, Callable, Optional, TypeVar, Union

from odin import exceptions
from odin.utils.ipv6 import is_valid_ipv6_address

EMPTY_VALUES = (None, "", [], (), {})


class RegexValidator:
    """Validate a regular expression."""

    regex = r""
    message = "Enter a valid value."
    code = "invalid"
    description: Optional[str] = None

    def __init__(
        self,
        regex: Union[str, re.Pattern] = None,
        message: str = None,
        code: str = None,
        description: str = None,
    ):
        if regex is not None:
            self.regex = regex
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code
        if description is not None:
            self.description = description

        # Compile the regex if it was not passed pre-compiled.
        if isinstance(self.regex, str):
            self.regex = re.compile(self.regex)

    def __call__(self, value):
        """Validates that the input matches the regular expression."""
        if not self.regex.search(value):
            raise exceptions.ValidationError(self.message, code=self.code)

    def __str__(self):
        """Generate str (used by sphinx for documentation)."""
        return (self.description or "{type_name}({pattern})").format(
            type_name=type(self).__name__, pattern=self.regex.pattern
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
    message = "Ensure this value is %(limit_value)s (it is %(show_value)s)."
    code = "limit_value"
    description = "Value is a {limit_value}."

    __slots__ = ("limit_value",)

    def __init__(self, limit_value):
        self.limit_value = limit_value

    def __call__(self, value):
        cleaned = self.clean(value)
        params = {"limit_value": self.limit_value, "show_value": cleaned}
        if self.compare(cleaned, self.limit_value):
            raise exceptions.ValidationError(
                self.message % params, code=self.code, params=params
            )

    def __str__(self):
        """Generate str (used by sphinx for documentation)."""
        return self.description.format(
            type_name=type(self).__name__, limit_value=self.limit_value
        )

    def compare(self, a, b):
        return a is not b

    def clean(self, value):
        return value


class MaxValueValidator(BaseValidator):
    """Validate value is less than a max value."""

    message = "Ensure this value is less than or equal to %(limit_value)s."
    code = "max_value"
    description = "Value is less than or equal to {limit_value}."

    def compare(self, a, b):
        return a > b


class MinValueValidator(BaseValidator):
    """Validate value is greater than a min value."""

    message = "Ensure this value is greater than or equal to %(limit_value)s."
    code = "min_value"
    description = "Value is greater than or equal to {limit_value}."

    def compare(self, a, b):
        return a < b


class LengthValidator(BaseValidator):
    """Validate value is has length of value."""

    message = (
        "Ensure this values length is exactly %(limit_value)d (it has %(show_value)d)."
    )
    code = "length"
    description = "Values length is {limit_value}."

    def compare(self, a, b):
        return a != b

    def clean(self, value):
        return len(value)


class MaxLengthValidator(LengthValidator):
    message = (
        "Ensure this values length is at most %(limit_value)d (it has %(show_value)d)."
    )
    code = "max_length"
    description = "Values length is at most {limit_value}."

    def compare(self, a, b):
        return a > b


class MinLengthValidator(LengthValidator):
    message = (
        "Ensure this values length is at least %(limit_value)d (it has %(show_value)d)."
    )
    code = "min_length"
    description = "Values length is at least {limit_value}."

    def compare(self, a, b):
        return a < b


class SimpleValidator:
    """Wrapper around a callable to provide simple validation."""

    __slots__ = ("assertion", "message", "code", "description")

    def __init__(
        self,
        assertion: Callable[[Any], bool],
        message: str,
        code: str,
        description: str = None,
    ):
        self.assertion = assertion
        self.message = message
        self.code = code
        self.description = description

    def __call__(self, value):
        params = {"show_value": value}
        if not self.assertion(value):
            raise exceptions.ValidationError(
                self.message % params, code=self.code, params=params
            )

    def __str__(self):
        """Generate str (used by sphinx for documentation)."""
        return (
            self.description
            or (self.assertion.__doc__ or self.assertion.__name__).strip()
        )


_A = TypeVar("_A", bound=Callable[[Any], bool])


def simple_validator(
    assertion: Union[_A, Callable[[_A], _A]] = None,
    *,
    message: str = "The supplied value is invalid",
    code: str = "invalid",
    description: str = None,
):
    """
    Create a simple validator.

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

    def inner(func):
        return SimpleValidator(func, message, code, description)

    if assertion:
        return inner(assertion)
    else:
        return inner


class IPv4Address(RegexValidator):
    """Validate an IPv4 address."""

    regex = r"^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|[0-1]?[0-9]?[0-9])){3}\Z"
    message = "Enter a valid IPv4 address."
    description = "Value is an IPv4 Address."


validate_ipv4_address = IPv4Address()


@simple_validator(message="Enter a valid IPv6 address")
def validate_ipv6_address(value):
    """Value is a valid IPv6 Address."""
    return is_valid_ipv6_address(value)


def validate_ipv46_address(value):
    """Value is either a valid IPv4 or IPv6 address."""
    try:
        validate_ipv4_address(value)
    except exceptions.ValidationError:
        try:
            validate_ipv6_address(value)
        except exceptions.ValidationError:
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
        r"\[([A-f0-9:.]+)\]\Z",
        re.IGNORECASE,
    )
    domain_whitelist = ["localhost"]

    def __init__(self, message=None, code=None, whitelist=None):
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code
        if whitelist is not None:
            self.domain_whitelist = whitelist

    def __str__(self):
        """Generate str (used by sphinx for documentation)."""
        return "Value is a valid Email address."

    def __call__(self, value):
        if not value or "@" not in value:
            raise exceptions.ValidationError(self.message, code=self.code)

        user_part, domain_part = value.rsplit("@", 1)

        if not self.user_regex.match(user_part):
            raise exceptions.ValidationError(self.message, code=self.code)

        if domain_part not in self.domain_whitelist and not self.validate_domain_part(
            domain_part
        ):
            # Try for possible IDN domain-part
            try:
                domain_part = domain_part.encode("idna").decode("ascii")
                if self.validate_domain_part(domain_part):
                    return
            except UnicodeError:
                pass
            raise exceptions.ValidationError(self.message, code=self.code)

    def validate_domain_part(self, domain_part):
        if self.domain_regex.match(domain_part):
            return True

        literal_match = self.literal_regex.match(domain_part)
        if literal_match:
            ip_address = literal_match.group(1)
            try:
                validate_ipv46_address(ip_address)
                return True
            except exceptions.ValidationError:
                pass


validate_email_address = EmailValidator()
