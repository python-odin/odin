import copy
import datetime
import enum
import pathlib
import re
import uuid
from collections.abc import Sequence
from functools import cached_property
from typing import Any, TypeVar

from odin import datetimeutil, exceptions, registration
from odin.utils import getmeta
from odin.validators import (
    EMPTY_VALUES,
    MaxLengthValidator,
    MaxValueValidator,
    MinValueValidator,
    validate_email_address,
    validate_ipv4_address,
    validate_ipv6_address,
    validate_ipv46_address,
    validate_url,
)

from .base import BaseField

__all__ = (
    "NotProvided",
    "NotProvidedType",
    "BaseField",
    "Field",
    "BooleanField",
    "StringField",
    "UrlField",
    "IntegerField",
    "FloatField",
    "DateField",
    "TimeField",
    "NaiveTimeField",
    "DateTimeField",
    "NaiveDateTimeField",
    "HttpDateTimeField",
    "TimeStampField",
    "EmailField",
    "IPv4Field",
    "IPv6Field",
    "IPv46Field",
    "ListField",
    "UUIDField",
    "DictField",
    "ObjectField",
    "ArrayField",
    "TypedArrayField",
    "TypedListField",
    "TypedDictField",
    "TypedObjectField",
    "EnumField",
    "PathField",
    "RegexField",
)


class NotProvided:
    pass


NotProvidedType = type[NotProvided]

# Backwards compatibility
NOT_PROVIDED = NotProvided


class Field(BaseField):
    """Base class for fields."""

    default_validators = []
    default_error_messages = {
        "invalid_choice": "Value %r is not a valid choice.",
        "null": "This field cannot be null.",
        "required": "This field is required.",
    }
    data_type_name = None
    empty_values = EMPTY_VALUES

    __slots__ = (
        "null",
        "default",
        "use_default_if_not_provided",
        "validators",
        "is_attribute",
        "key",
        "choices",
        "error_messages",
        "resource",
    )

    def __init__(  # noqa: PLR0913
        self,
        verbose_name: str = None,
        verbose_name_plural: str = None,
        name: str = None,
        null: bool = False,
        choices: Sequence[tuple[Any, str]] | None = None,
        use_default_if_not_provided: bool = False,
        default=NotProvided,
        help_text: str = "",
        validators: Sequence = None,
        error_messages: dict[str, str] = None,
        is_attribute: bool = False,
        doc_text: str = "",
        key: bool = False,
    ):
        """
        Initialisation of a Field.

        :param verbose_name: Display name of field.
        :param verbose_name_plural: Plural display name of field.
        :param name: Name of the serialised field.
        :param null: This value can be null/None.
        :param choices: Collection of valid choices for this field.
        :param use_default_if_not_provided: If a value is not provided during mapping, use the default value.
        :param default: Default value for this field.
        :param help_text: Deprecated; Help text to describe this field.
        :param validators: Additional validators, these should be a callable that takes a single value.
        :param error_messages: Dictionary that overrides error messages (or provides additional messages for custom
            validation).
        :param is_attribute: Special flag for codecs that support attributes on nodes (ie XML)
        :param doc_text: Documentation for the field, replaces help text
        :param key: Mark this field as a key field (used to generate a unique identifier).

        """
        super().__init__(verbose_name, verbose_name_plural, name, doc_text or help_text)

        self.null = null
        self.default = default
        self.use_default_if_not_provided = use_default_if_not_provided
        self.validators = self.default_validators + (validators or [])
        self.is_attribute = is_attribute
        self.key = key

        # Check choice's match the spec
        if choices and not all(
            isinstance(choice, tuple | list) and len(choice) == 2  # noqa: PLR2004
            for choice in choices
        ):
            msg = "`choices` is required to be a value, doc string pair"
            raise ValueError(msg)
        self.choices = choices

        messages = {}
        for c in reversed(self.__class__.__mro__):
            messages.update(getattr(c, "default_error_messages", {}))
        messages.update(error_messages or {})
        self.error_messages = messages

        self.resource = None

    def __deepcopy__(self, memodict):
        # We don't have to deepcopy very much here, since most things are not
        # intended to be altered after initial creation.
        obj = copy.copy(self)
        memodict[id(self)] = obj
        return obj

    @cached_property
    def choice_values(self):
        """Choice values to allow choices to simplify checking if a choice is valid."""
        if self.choices is not None:
            return tuple(c[0] for c in self.choices)

    @property
    def choices_doc_text(self) -> Sequence[tuple[str, str]]:
        """Choices converted for documentation purposes."""
        return self.choices

    def contribute_to_class(self, cls, name: str):
        """Contribute value this field to a resource class."""
        meta = getmeta(cls)
        self.set_attributes_from_name(name, meta.field_name_format)
        self.resource = cls
        meta.add_field(self)

    def to_python(self, value):
        """
        Converts the input value into the expected Python data type, raising
        ``odin.exceptions.ValidationError`` if the data can't be converted.
        Returns the converted value. Subclasses should override this.
        """
        raise NotImplementedError()

    def run_validators(self, value):
        """Execute validators against supplied value."""
        if value in self.empty_values:
            return

        errors = []
        for v in self.validators:
            try:
                v(value)
            except registration.get_validation_error_list() as e:
                handler = registration.get_validation_error_handler(e)
                handler(e, self, errors)
        if errors:
            raise exceptions.ValidationError(errors)

    def validate(self, value):
        """Validate a supplied value."""
        if (
            self.choice_values
            and (value not in self.empty_values)
            and (value not in self.choice_values)
        ):
            msg = self.error_messages["invalid_choice"] % value
            raise exceptions.ValidationError(msg)

        if not self.null and value is None:
            raise exceptions.ValidationError(self.error_messages["null"])

    def clean(self, value):
        """
        Convert the value's type and run validation. Validation errors
        from to_python and validate are propagated. The correct value is
        returned if no error is raised.
        """
        if value is NotProvided:
            value = self.get_default() if self.use_default_if_not_provided else None
        value = self.to_python(value)
        self.validate(value)
        self.run_validators(value)
        return value

    def has_default(self):
        """Returns a bool of whether this field has a default value."""
        return self.default is not NotProvided

    def get_default(self):
        """Returns the default value for this field."""
        if self.has_default():
            if callable(self.default):
                return self.default()
            return self.default
        return None

    def value_to_object(self, obj, data):
        """Assign a value to an object."""
        setattr(obj, self.attname, data)


class BooleanField(Field):
    """Field that must contain a boolean value."""

    default_error_messages = {"invalid": "'%s' value must be either True or False."}
    true_strings = ("t", "true", "y", "yes", "on", "1", "✓")
    false_strings = ("f", "false", "n", "no", "off", "0")
    data_type_name = "Boolean"

    def to_python(self, value):
        if value is None:
            return None
        if value in (True, False):
            # if value is 1 or 0 then it's equal to True or False, but we want
            # to return a true bool for semantic reasons.
            return bool(value)
        if isinstance(value, str):
            lvalue = value.lower()
            if lvalue in self.true_strings:
                return True
            if lvalue in self.false_strings:
                return False
        msg = self.error_messages["invalid"] % str(value)
        raise exceptions.ValidationError(msg)


class StringField(Field):
    """
    A string.

    StringField has two extra arguments:

    :py:attr:`StringField.empty`
        The string can be empty. This is similar to None but captures an empty string in addition to ``None``.
        The default state of this flag is ``False``.

    :py:attr:`StringField.max_length`
        The maximum length (in characters) of the field. The ``max_length`` value is enforced Odin’s validation.
    """

    data_type_name = "String"

    def __init__(self, max_length: int = None, empty: bool = None, **options):
        super().__init__(**options)
        self.max_length = max_length

        # Mirror null is not explicitly defined
        if empty is None:
            empty = options.get("null", False)
        self.empty = empty

        if max_length is not None:
            self.validators.append(MaxLengthValidator(max_length))

    def to_python(self, value):
        if value is None or isinstance(value, str):
            return value
        return str(value)

    def validate(self, value):
        if not self.empty and value == "":
            raise exceptions.ValidationError(self.error_messages["null"])

        super().validate(value)


class UrlField(StringField):
    """Field that must create a URL."""

    data_type_name = "URL"

    def __init__(self, **options):
        options.setdefault("validators", []).append(validate_url)
        super().__init__(**options)


class ScalarField(Field):
    scalar_type = int

    def __init__(self, min_value=None, max_value=None, **options):
        super().__init__(**options)
        self.min_value = min_value
        if min_value is not None:
            self.validators.append(MinValueValidator(min_value))
        self.max_value = max_value
        if max_value is not None:
            self.validators.append(MaxValueValidator(max_value))

    def to_python(self, value):
        if value in self.empty_values:
            return
        try:
            return self.scalar_type(value)

        except (TypeError, ValueError):
            msg = self.error_messages["invalid"] % value
            raise exceptions.ValidationError(msg) from None


class IntegerField(ScalarField):
    default_error_messages = {
        "invalid": "'%s' value must be a integer.",
    }
    data_type_name = "Integer"


class FloatField(ScalarField):
    default_error_messages = {
        "invalid": "'%s' value must be a float.",
    }
    data_type_name = "Float"
    scalar_type = float


class _IsoFormatMixin(BaseField):
    def as_string(self, value):
        """
        Generate a string representation of a field.

        :param value:
        :rtype: str

        """
        if value:
            return value.isoformat()


class DateField(_IsoFormatMixin, Field):
    """
    Field that handles date values encoded as a string.

    The format of the string is that defined by ISO-8601.

    """

    default_error_messages = {
        "invalid": "Not a valid date string.",
    }
    data_type_name = "ISO-8601 Date"

    def to_python(self, value):
        if value in self.empty_values:
            return
        if isinstance(value, datetime.datetime):
            return value.date()
        if isinstance(value, datetime.date):
            return value
        try:
            return datetimeutil.parse_iso_date_string(value)
        except ValueError:
            pass
        msg = self.error_messages["invalid"]
        raise exceptions.ValidationError(msg)


class TimeField(_IsoFormatMixin, Field):
    """
    Field that handles time values encoded as a string.

    The format of the string is that defined by ISO-8601.

    Use the ``assume_local`` flag to customise how naive (datetime values with
    no timezone) are handled and also how dates are decoded. If
    ``assume_local`` is True naive dates are assumed to represent the current
    system timezone.

    """

    default_error_messages = {
        "invalid": "Not a valid time string.",
    }
    data_type_name = "ISO-8601 Time"

    def __init__(self, assume_local: bool = False, **options):
        super().__init__(**options)
        self.assume_local = assume_local

    def to_python(self, value):
        if value in self.empty_values:
            return
        if isinstance(value, datetime.time):
            return value
        default_timezone = datetimeutil.local if self.assume_local else datetimeutil.utc
        try:
            return datetimeutil.parse_iso_time_string(value, default_timezone)
        except ValueError:
            pass
        msg = self.error_messages["invalid"]
        raise exceptions.ValidationError(msg)


class NaiveTimeField(_IsoFormatMixin, Field):
    """
    Field that handles time values encoded as a string.

    The format of the string is that defined by ISO-8601.

    The naive time field differs from :py:`~TimeField` in the handling of the
    timezone, a timezone will not be applied if one is not specified.

    Use the ``ignore_timezone`` flag to have any timezone information ignored
    when decoding the time field.

    """

    default_error_messages = {
        "invalid": "Not a valid time string.",
    }
    data_type_name = "Naive ISO-8601 Time"

    def __init__(self, ignore_timezone=False, **options):
        super().__init__(**options)
        self.ignore_timezone = ignore_timezone

    def to_python(self, value):
        if value in self.empty_values:
            return
        if isinstance(value, datetime.time):
            if value.tzinfo and self.ignore_timezone:
                return value.replace(tzinfo=None)
            return value
        default_timezone = datetimeutil.IgnoreTimezone if self.ignore_timezone else None
        try:
            return datetimeutil.parse_iso_time_string(value, default_timezone)
        except ValueError:
            pass
        msg = self.error_messages["invalid"]
        raise exceptions.ValidationError(msg)

    def prepare(self, value):
        """
        Prepare for serialisation

        :param value:
        :return:

        """
        if (value is not None) and self.ignore_timezone and (value.tzinfo is not None):
            # Strip the timezone
            value = value.replace(tzinfo=None)
        return value


class DateTimeField(_IsoFormatMixin, Field):
    """
    Field that handles datetime values encoded as a string.

    The format of the string is that defined by ISO-8601.

    Use the ``assume_local`` flag to customise how naive (datetime values
    with no timezone) are handled and also how dates are decoded. If
    ``assume_local`` is True naive dates are assumed to represent the current
    system timezone.

    """

    default_error_messages = {
        "invalid": "Not a valid datetime string.",
    }
    data_type_name = "ISO-8601 DateTime"

    def __init__(self, assume_local: bool = False, **options):
        super().__init__(**options)
        self.assume_local = assume_local

    def to_python(self, value):
        if value in self.empty_values:
            return
        if isinstance(value, datetime.datetime):
            return value
        default_timezone = datetimeutil.local if self.assume_local else datetimeutil.utc
        try:
            return datetimeutil.parse_iso_datetime_string(value, default_timezone)
        except ValueError:
            pass
        msg = self.error_messages["invalid"]
        raise exceptions.ValidationError(msg)


class NaiveDateTimeField(_IsoFormatMixin, Field):
    """
    Field that handles datetime values encoded as a string.

    The format of the string is that defined by ISO-8601.

    The naive time field differs from :py:`~DateTimeField` in the handling of the
    timezone, a timezone will not be applied if one is not specified.

    Use the ``ignore_timezone`` flag to have any timezone information ignored
    when decoding the time field.

    """

    default_error_messages = {
        "invalid": "Not a valid datetime string.",
    }
    data_type_name = "Naive ISO-8601 DateTime"

    def __init__(self, ignore_timezone=False, **options):
        super().__init__(**options)
        self.ignore_timezone = ignore_timezone

    def to_python(self, value):
        if value in self.empty_values:
            return
        if isinstance(value, datetime.datetime):
            if value.tzinfo and self.ignore_timezone:
                return value.replace(tzinfo=None)
            return value
        default_timezone = datetimeutil.IgnoreTimezone if self.ignore_timezone else None
        try:
            return datetimeutil.parse_iso_datetime_string(value, default_timezone)
        except ValueError:
            pass
        msg = self.error_messages["invalid"]
        raise exceptions.ValidationError(msg)

    def prepare(self, value):
        """
        Prepare for serialisation

        :param value:
        :return:

        """
        if (value is not None) and self.ignore_timezone and (value.tzinfo is not None):
            # Strip the timezone
            value = value.replace(tzinfo=None)
        return value


class HttpDateTimeField(Field):
    """
    Field that handles datetime values encoded as a string.

    The format of the string is that defined by ISO-1123.

    """

    default_error_messages = {
        "invalid": "Not a valid HTTP datetime string.",
    }
    data_type_name = "ISO-1123 DateTime"

    def to_python(self, value):
        if value in self.empty_values:
            return
        if isinstance(value, datetime.datetime):
            return value
        try:
            return datetimeutil.parse_http_datetime_string(value)
        except ValueError:
            pass
        msg = self.error_messages["invalid"]
        raise exceptions.ValidationError(msg)

    def as_string(self, value):
        """
        Generate a string representation of a field.

        :param value:
        :rtype: str

        """
        if value is not None:
            return datetimeutil.to_http_datetime_string(value)


class TimeStampField(Field):
    """
    Field that handles datetime values encoding as the number of seconds since the UNIX epoch.

    A UNIX timestamp should always be calculated relative to UTC.

    """

    default_error_messages = {
        "invalid": "Not a valid UNIX timestamp.",
    }
    data_type_name = "Integer"

    def to_python(self, value):
        if value in self.empty_values:
            return
        if isinstance(value, datetime.datetime):
            return value
        try:
            return datetime.datetime.fromtimestamp(int(value), tz=datetimeutil.utc)
        except ValueError:
            pass
        msg = self.error_messages["invalid"]
        raise exceptions.ValidationError(msg)

    def prepare(self, value):
        """Prepare for value for serialisation"""
        if value in self.empty_values:
            return
        if isinstance(value, int):
            return int(value)
        if isinstance(value, datetime.datetime):
            return datetimeutil.to_timestamp(value)


class DictField(Field):
    default_error_messages = {
        "invalid": "Must be a dict.",
    }
    data_type_name = "Dict"
    empty_values = (None, "", [], ())

    def __init__(self, **options):
        options.setdefault("default", dict)
        super().__init__(**options)

    def __iter__(self):
        # This does nothing but it does prevent inspections from complaining.
        return None  # NoQA

    def to_python(self, value):
        if value is None:
            return value
        try:
            val = dict(value)
            return val

        except (TypeError, ValueError):
            msg = self.error_messages["invalid"]
            raise exceptions.ValidationError(msg) from None


ObjectField = DictField


class ListField(Field):
    default_error_messages = {
        "invalid": "Must be an array.",
    }
    data_type_name = "List"
    empty_values = (None, "", {}, ())

    def __init__(self, **options):
        options.setdefault("default", list)
        super().__init__(**options)

    def __iter__(self):
        # This does nothing but it does prevent inspections from complaining.
        return None  # NoQA

    def to_python(self, value):
        if value is None:
            return value
        if isinstance(value, list | tuple):
            return value
        msg = self.error_messages["invalid"]
        raise exceptions.ValidationError(msg)


ArrayField = ListField


class TypedListField(ListField):
    """Field that handles a list of a specific type."""

    @staticmethod
    def data_type_name(instance):
        type_name = instance.field.data_type_name
        if callable(type_name):
            type_name = type_name(instance.field)
        return f"List<{type_name}>"

    def __init__(self, field: Field, **options):
        """Initialise the typed list field."""
        self.field = field
        super().__init__(**options)

    @property
    def choices_doc_text(self) -> Sequence[tuple[Any, str]]:
        """Generate choices for documentation purposes."""
        if self.choices:
            return self.choices
        if hasattr(self.field, "choices_doc_text"):
            return self.field.choices_doc_text
        return self.field.choices

    def to_python(self, value):
        """Convert the value to a list of the specified type."""
        value = super().to_python(value)
        if not value:
            return value

        value_list = []
        errors = {}
        field_to_python = self.field.to_python
        for idx, item in enumerate(value):
            try:
                value_list.append(field_to_python(item))
            except exceptions.ValidationError as ve:
                errors[str(idx)] = ve.error_messages

        if errors:
            raise exceptions.ValidationError(errors)

        return value_list

    def validate(self, value):
        """Validate each item against field"""
        super().validate(value)
        if value:
            field_validate = self.field.validate

            errors = {}
            for idx, item in enumerate(value):
                try:
                    field_validate(item)
                except exceptions.ValidationError as ve:
                    errors[str(idx)] = ve.error_messages

            if errors:
                raise exceptions.ValidationError(errors)

        return value

    def run_validators(self, value):
        """Run validators against each item in the field"""
        super().run_validators(value)
        if value:
            field_run_validators = self.field.run_validators

            errors = {}
            for idx, item in enumerate(value):
                try:
                    field_run_validators(item)
                except exceptions.ValidationError as ve:
                    errors[str(idx)] = ve.error_messages

            if errors:
                raise exceptions.ValidationError(errors)

        return value

    def prepare(self, value):
        """Prepare list for serialisation."""
        if isinstance(value, tuple | list):
            prepare = self.field.prepare
            return [prepare(i) for i in value]
        return value


TypedArrayField = TypedListField


class TypedDictField(DictField):
    """
    Dict field with both key and value fixed to a specific types. By default the key field is assumed to be a string.

    Usage::

        # Dict with key and value fields as string.
        TypedDictField(key_field=StringField(), value_field=StringField())

    """

    @staticmethod
    def data_type_name(instance):
        key_type_name = instance.key_field.data_type_name
        if callable(key_type_name):
            key_type_name = key_type_name(instance.key_field)

        value_type_name = instance.value_field.data_type_name
        if callable(value_type_name):
            value_type_name = value_type_name(instance.value_field)

        return f"Dict<{key_type_name}, {value_type_name}>"

    default_key_field = StringField()

    def __init__(self, value_field, key_field=default_key_field, **options):
        self.key_field = key_field
        self.value_field = value_field
        super().__init__(**options)

    def to_python(self, value):
        """Convert the value to a dict of the specified type."""
        value = super().to_python(value)
        if not value:
            return value

        value_dict = {}
        key_errors = []
        value_errors = {}
        for key, val in value.items():
            try:
                key = self.key_field.to_python(key)  # noqa: PLW2901
            except exceptions.ValidationError as ve:
                key_errors += ve.error_messages

            # If we have key errors no point checking values.
            if key_errors:
                continue

            try:
                value_dict[key] = self.value_field.to_python(val)
            except exceptions.ValidationError as ve:
                value_errors[key] = ve.error_messages

        if key_errors:
            raise exceptions.ValidationError(key_errors)
        if value_errors:
            raise exceptions.ValidationError(value_errors)

        return value_dict

    def validate(self, value):
        """Validate value."""
        super().validate(value)

        if value in self.empty_values:
            return

        key_errors = []
        value_errors = {}
        for key, val in value.items():
            try:
                self.key_field.validate(key)
            except exceptions.ValidationError as ve:
                key_errors += ve.error_messages

            # If we have key errors no point checking values
            if key_errors:
                continue

            try:
                self.value_field.validate(val)

            except exceptions.ValidationError as ve:
                value_errors[key] = ve.error_messages

        if key_errors:
            raise exceptions.ValidationError(key_errors)
        if value_errors:
            raise exceptions.ValidationError(value_errors)

    def run_validators(self, value):
        """Run validators against value."""
        super().run_validators(value)

        if value in self.empty_values:
            return

        key_errors = []
        value_errors = {}
        for key, val in value.items():
            try:
                key = self.key_field.run_validators(key)  # noqa: PLW2901
            except exceptions.ValidationError as ve:
                key_errors += ve.error_messages

            # If we have key errors no point checking values.
            if key_errors:
                continue

            try:
                self.value_field.run_validators(val)
            except exceptions.ValidationError as ve:
                value_errors[key] = ve.error_messages

        if key_errors:
            raise exceptions.ValidationError(key_errors)
        if value_errors:
            raise exceptions.ValidationError(value_errors)

    def prepare(self, value):
        """Prepare list for serialisation."""
        if isinstance(value, dict):
            prepare_key = self.key_field.prepare
            prepare_value = self.value_field.prepare
            return {prepare_key(k): prepare_value(v) for k, v in value.items()}
        return value


TypedObjectField = TypedDictField


class EmailField(StringField):
    """An Email address.

    Validates that a string represents a valid Email address.
    """

    data_type_name = "Email"

    def __init__(self, **options):
        """Initialise the field."""
        options.setdefault("validators", []).append(validate_email_address)
        super().__init__(**options)


class IPv4Field(StringField):
    """An IPv4 address.

    Validates that a string represents a valid IPv4 address format.
    """

    data_type_name = "IPv4"

    def __init__(self, **options):
        """Initialise the field."""
        options.setdefault("validators", []).append(validate_ipv4_address)
        super().__init__(**options)


class IPv6Field(StringField):
    """An IPv6 address.

    Validates that a string represents a valid IPv6 address format.
    """

    data_type_name = "IPv6"

    def __init__(self, **options):
        """Initialise the field."""
        options.setdefault("validators", []).append(validate_ipv6_address)
        super().__init__(**options)


class IPv46Field(StringField):
    """An IPv4 or IPv6 address.

    Validates that a string represents a valid IPv4 or IPv6 address format.
    """

    data_type_name = "IPv46"

    def __init__(self, **options):
        """Initialise the field."""
        options.setdefault("validators", []).append(validate_ipv46_address)
        super().__init__(**options)


class UUIDField(Field):
    """An universally unique identifier.

    Validates that the string represents a universally unique identifier.
    """

    data_type_name = "UUID"

    def to_python(self, value):
        """Convert the value to a UUID."""
        if value is None:
            return

        if isinstance(value, uuid.UUID):
            return value

        elif isinstance(value, bytes):
            if len(value) == 16:  # noqa: PLR2004 length of a valid UUID
                return uuid.UUID(bytes=value)

            try:
                value = value.decode("utf-8")
            except UnicodeDecodeError as e:
                raise exceptions.ValidationError(e.args[0], code="invalid") from None

        elif isinstance(value, int):
            try:
                return uuid.UUID(int=value)
            except ValueError as e:
                raise exceptions.ValidationError(e.args[0], code="invalid") from None

        elif isinstance(value, tuple | list):
            try:
                return uuid.UUID(fields=value)
            except ValueError as e:
                raise exceptions.ValidationError(e.args[0], code="invalid") from None

        elif not isinstance(value, str):
            value = str(value)

        try:
            return uuid.UUID(value)
        except ValueError as e:
            raise exceptions.ValidationError(e.args[0], code="invalid") from None


ET = TypeVar("ET", bound=enum.Enum)


class EnumField(Field):
    """Field for handling Python enums."""

    data_type_name = "Enum"

    def __init__(self, enum_type: type[ET], **options):
        """Initialise the field."""

        # Generate choices structure from choices
        choices = options.pop("choices", None)
        options["choices"] = tuple((e, e.name) for e in choices or enum_type)

        super().__init__(**options)
        self.enum_type = enum_type

    @property
    def choices_doc_text(self):
        """Choices converted for documentation purposes."""
        return tuple((v.value, n) for v, n in self.choices)

    def to_python(self, value) -> ET | None:
        """Convert the value to an enum."""
        if value is None:
            return

        # Attempt to convert
        try:
            return self.enum_type(value)
        except ValueError:
            # If value is an empty string return None
            # Do this check here to support enums that define an option using
            # an empty string.
            if value == "":
                return
            raise exceptions.ValidationError(
                self.error_messages["invalid_choice"] % value
            ) from None

    def prepare(self, value: ET | None):
        """Prepare enum for serialisation."""
        if (value is not None) and isinstance(value, self.enum_type):
            return value.value


class PathField(Field):
    """Field for handling Python Paths"""

    default_error_messages = {
        "invalid": "Value %s is not a valid path.",
    }
    data_type_name = "Path"

    def to_python(self, value) -> pathlib.Path | None:
        """Convert the value to a Path."""
        if value is None:
            return

        # Attempt to convert
        try:
            return pathlib.Path(value)

        except (ValueError, TypeError):
            raise exceptions.ValidationError(
                self.error_messages["invalid"] % value
            ) from None

    def prepare(self, value: str | None):
        """Prepare path for serialisation."""
        if isinstance(value, pathlib.Path):
            return value.as_posix()


class RegexField(Field):
    """
    Field for handling regular expressions.

    Note this field will compile a regular expression into a pattern.

    Regular expressions use the Python syntax.
    """

    default_error_messages = {
        "invalid": "Value '%s' is not a valid regular expression.",
        "syntax": "Value '%s' contains invalid syntax: %s.",
    }
    data_type_name = "Regex"

    def to_python(self, value) -> re.Pattern | None:
        """Convert the value to a regular expression."""
        if value is None:
            return

        try:
            return re.compile(value)

        except TypeError:
            raise exceptions.ValidationError(
                self.error_messages["invalid"] % value
            ) from None

        except re.error as ex:
            raise exceptions.ValidationError(
                self.error_messages["syntax"] % (value, ex)
            ) from None

    def prepare(self, value: re.Pattern | None):
        """Prepare regular expression for serialisation."""
        if isinstance(value, re.Pattern):
            return value.pattern
