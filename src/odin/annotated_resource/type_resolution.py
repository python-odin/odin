"""Methods for resolving types to fields."""

import datetime
import enum
import functools
import pathlib
import re
import uuid
from types import UnionType
from typing import Annotated, Any, Final, Union, get_args, get_origin

import odin

from ..exceptions import ResourceDefError
from ..fields import (
    BaseField,
    BooleanField,
    DateField,
    DateTimeField,
    DictField,
    EmailField,
    Field,
    FloatField,
    IntegerField,
    IPv4Field,
    IPv6Field,
    IPv46Field,
    ListField,
    NotProvided,
    PathField,
    RegexField,
    StringField,
    TimeField,
    TypedDictField,
    TypedListField,
    UrlField,
    UUIDField,
)
from ..fields.composite import DictOf, ListOf
from ..fields.virtual import ConstantField
from ..resources import ResourceBase
from .special_fields import AnyField
from .type_aliases import Choices, Email, IPv4, IPv6, IPv46, Url, Validator


class Options:
    """Define options for a field"""

    __slots__ = (
        "field_type",
        "base_args",
        "field_args",
        "extra_args",
    )

    def __init__(  # noqa: PLR0913
        self,
        default: ... = NotProvided,
        field_type: type[Field] = None,
        *,
        verbose_name: str = None,
        verbose_name_plural: str = None,
        name: str = None,
        validators: list[Validator] = None,
        choices: Choices | None = None,
        use_default_if_not_provided: bool = True,
        error_messages: dict[str, str] | None = None,
        doc_text: str = "",
        is_attribute: bool = False,
        key: bool = False,
        **extra_args: ...,
    ):
        self.field_type = field_type
        self.base_args = {
            "verbose_name": verbose_name,
            "verbose_name_plural": verbose_name_plural,
            "name": name,
            "doc_text": doc_text,
            "is_attribute": is_attribute,
            "key": key,
        }
        self.base_args.update(extra_args)
        self.field_args = {
            "choices": choices,
            "use_default_if_not_provided": use_default_if_not_provided,
            "validators": validators or [],
            "error_messages": error_messages,
        }
        if default not in (None, NotProvided):
            self.field_args["default"] = default

    def __repr__(self):
        summary = ", ".join(
            f"{key}={val!r}" for key, val in self._kwargs().items() if val is not None
        )
        field_type = self.actual_field_type
        return (
            f"Options({field_type}, {summary})" if field_type else f"Options({summary})"
        )

    @property
    def actual_field_type(self):
        """Actual field type."""
        field_type = self.field_type
        return (
            field_type.func if isinstance(field_type, functools.partial) else field_type
        )

    @property
    def is_field_type_valid(self) -> bool:
        """Have a valid field type."""
        field_type = self.actual_field_type
        return field_type is not None and issubclass(field_type, Field)

    def _kwargs(self):
        """Build kwargs used to instantiate field"""
        if self.is_field_type_valid:
            return {**self.base_args, **self.field_args}
        return self.base_args

    def _improve_error(self, ex: TypeError):
        """Attempt to provide more context for the error"""
        message = str(ex)

        checks = [
            "Field.__init__()",
            "VirtualField.__init__()",
        ]
        if name := getattr(self.field_type, "__name__", None):
            checks.append(f"{name}.__init__()")

        for check in checks:
            if message.startswith(check):
                msg = f"{self.field_type.__name__}.__init__(){message[len(check) :]}"
                raise ResourceDefError(msg)

    def construct_field(self) -> Field:
        """Instantiate field object"""
        if self.field_type:
            try:
                return self.field_type(**self._kwargs())
            except TypeError as ex:
                self._improve_error(ex)
                raise

        msg = f"Field type `{self.base_args.get('name', 'Unknown!')}` could not be resolved"
        raise ResourceDefError(msg)


SIMPLE_TYPE_MAP: dict[type, type[Field] | functools.partial] = {
    bool: BooleanField,
    datetime.date: DateField,
    datetime.datetime: DateTimeField,
    dict: DictField,
    Email: EmailField,
    float: FloatField,
    int: IntegerField,
    IPv4: IPv4Field,
    IPv6: IPv6Field,
    IPv46: IPv46Field,
    list: ListField,
    pathlib.Path: PathField,
    re.Pattern: RegexField,
    str: StringField,
    datetime.time: TimeField,
    Url: UrlField,
    uuid.UUID: UUIDField,
    Any: AnyField,
}


def _create_field_from_list_type(args: tuple, options: Options) -> BaseField:
    """Handle the various types of list."""
    if args:
        (tp,) = args
        # Use get origin to determine if value is also sub-scripted. This is
        # required as issubclass cannot be used on sub-scripted fields.
        if not (tp is Any or get_origin(tp)) and issubclass(tp, ResourceBase):
            options.field_args["resource"] = tp
            options.field_type = ListOf

        else:
            options.field_args["field"] = process_attribute(tp)
            options.field_type = TypedListField
    else:
        options.field_type = ListField

    return options.construct_field()


def _create_field_from_dict_type(args: tuple, options: Options) -> BaseField:
    """Handle the various types of mapping."""
    if args:
        key_field, value_field = args
        # Use get origin to determine if value is also sub-scripted. This is
        # required as issubclass cannot be used on sub-scripted fields.
        if not (get_origin(value_field) or value_field is Any) and issubclass(
            value_field, ResourceBase
        ):
            options.field_args["resource"] = value_field
            options.field_type = DictOf

        else:
            options.field_args["key_field"] = process_attribute(key_field)
            options.field_args["value_field"] = process_attribute(value_field)
            options.field_type = TypedDictField

    else:
        options.field_type = DictField

    return options.construct_field()


def _create_nullable_field(args, options: Options) -> BaseField:
    """Handle union fields."""

    type_none = type(None)

    tp, nullable = None, False
    for arg in args:
        if arg is type_none:
            nullable = True
        elif tp is None:
            tp = arg
        else:
            nullable = False
            break

    if not nullable or tp is None:
        msg = "Union type are only supported with a single type and None"
        raise ResourceDefError(msg)

    options.field_args["null"] = True
    return process_attribute(tp, options)


def _set_options_field_type(options: Options, tp: type):
    """Identify field type form a basic type."""

    if field_type := SIMPLE_TYPE_MAP.get(tp):
        options.field_type = field_type

    # Is a resource; resolve as DictAs
    elif issubclass(tp, ResourceBase):
        options.field_args["resource"] = tp
        options.field_type = odin.DictAs

    # Is an enum; resolve as EnumType
    elif issubclass(tp, enum.Enum):
        options.field_args["enum_type"] = tp
        options.field_type = odin.EnumField

    else:
        msg = f"Unable to resolve field for type {tp}"
        raise ResourceDefError(msg)


def _create_field_via_origin(origin, tp, options: Options) -> BaseField:
    if origin is Union or origin is UnionType:
        args = get_args(tp)
        return _create_nullable_field(args, options)

    if origin is Final:
        # Constant
        options.field_type = ConstantField
        if (value := options.field_args.get("default")) is None:
            msg = "Final fields require a value"
            raise ResourceDefError(msg)
        options.base_args["value"] = value
        return options.construct_field()

    # If type already defined skip lookup
    if options.is_field_type_valid:
        return options.construct_field()

    if issubclass(origin, list):
        return _create_field_from_list_type(get_args(tp), options)

    if issubclass(origin, dict):
        return _create_field_from_dict_type(get_args(tp), options)

    msg = f"Unable to resolve field for sub-scripted type {tp!r}"
    raise ResourceDefError(msg)


def _create_field_for_type(tp, options: Options) -> Field:
    # If type already defined skip lookup
    if options.is_field_type_valid:
        return options.construct_field()

    # Is a basic type
    if isinstance(tp, type):
        _set_options_field_type(options, tp)
    elif tp is Any:
        # For Python 3.10
        options.field_type = AnyField
    else:
        msg = f"Annotation is not a type instance {tp!r}"
        raise ResourceDefError(msg)

    return options.construct_field()


def _create_field_via_annotated(tp, value) -> BaseField:
    """Process an Annotated type."""

    if isinstance(value, Options):
        msg = "Options should included in the Annotation"
        raise ResourceDefError(msg)

    # Resolve sub-type and options
    tp, metadata = get_args(tp)
    if isinstance(metadata, Options):
        options = metadata
        options.field_args["default"] = value
    else:
        options = Options(value)

    if origin := get_origin(tp):
        return _create_field_via_origin(origin, tp, options)
    else:
        return _create_field_for_type(tp, options)


def process_attribute(
    tp: type,
    value: Options | Any = NotProvided,
    *,
    _base_field: type[BaseField] = BaseField,
) -> BaseField:
    """Process an individual attribute and generate a field based off values passed"""

    # Attribute is already a field object
    if isinstance(value, _base_field):
        return value

    if origin := get_origin(tp):
        if origin is Annotated:
            return _create_field_via_annotated(tp, value)

        options = value if isinstance(value, Options) else Options(value)
        return _create_field_via_origin(origin, tp, options)

    else:
        options = value if isinstance(value, Options) else Options(value)
        return _create_field_for_type(tp, options)
