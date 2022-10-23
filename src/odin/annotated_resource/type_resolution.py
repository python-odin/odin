import datetime
import enum
import pathlib
import typing
import uuid
from typing import Any, Sequence, Dict, Type, Union, get_origin, List

import odin
from .type_aliases import Validator, Choices, Email, IPv4, IPv6, IPv46, Url
from .. import ListOf, DictOf
from ..exceptions import ResourceDefError
from ..fields import (
    BaseField,
    Field,
    ListField,
    DictField,
    NotProvided,
    TypedListField,
    TypedDictField,
)
from ..resources import ResourceBase


class Options:
    """
    Define options for a field
    """

    __slots__ = (
        "field_type",
        "base_args",
        "field_args",
        "extra_args",
    )

    def __init__(
        self,
        default: Any = odin.NotProvided,
        field_type: Type[odin.BaseField] = None,
        *,
        verbose_name: str = None,
        verbose_name_plural: str = None,
        name: str = None,
        validators: Sequence[Validator] = None,
        choices: Choices = None,
        use_default_if_not_provided: bool = True,
        error_messages: Dict[str, str] = None,
        doc_text: str = "",
        is_attribute: bool = False,
        key: bool = False,
        **extra_args: Any,
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
            "default": default,
            "validators": validators,
            "error_messages": error_messages,
        }

    def _kwargs(self):
        """
        Build kwargs used to instantiate field
        """
        final_args = self.base_args
        if issubclass(self.field_type, Field):
            final_args.update(self.field_args)
        return final_args

    def _improve_error(self, ex: TypeError):
        """
        Attempt to provide more context for the error
        """
        message = str(ex)

        for check in (
            "Field.__init__()",
            "VirtualField.__init__()",
            f"{self.field_type.__name__}.__init__()",
        ):
            if message.startswith(check):
                raise ResourceDefError(
                    f"{self.field_type.__name__}.__init__(){message[len(check):]}"
                )

    def init_field(self):
        """
        Instantiate field object
        """
        if self.field_type:
            try:
                return self.field_type(**self._kwargs())
            except TypeError as ex:
                self._improve_error(ex)
                raise
        raise ResourceDefError("Field type could not be resolved")


SIMPLE_TYPE_MAP = {
    bool: odin.BooleanField,
    datetime.date: odin.DateField,
    datetime.datetime: odin.DateTimeField,
    dict: odin.DictField,
    Email: odin.EmailField,
    float: odin.FloatField,
    int: odin.IntegerField,
    IPv4: odin.IPv4Field,
    IPv6: odin.IPv6Field,
    IPv46: odin.IPv46Field,
    list: odin.ListField,
    pathlib.Path: odin.PathField,
    str: odin.StringField,
    datetime.time: odin.TimeField,
    Url: odin.UrlField,
    uuid.UUID: odin.UUIDField,
}


def _resolve_field_from_type(options: Options, type_: type):
    """
    Resolve a field from a basic type
    """
    if field_type := SIMPLE_TYPE_MAP.get(type_, None):
        options.field_type = field_type

    # Is a resource; resolve as DictAs
    elif issubclass(type_, ResourceBase):
        options.field_args["resource"] = type_
        options.field_type = odin.DictAs

    # Is an enum; resolve as EnumType
    elif issubclass(type_, enum.Enum):
        options.field_args["enum_type"] = type_
        options.field_type = odin.EnumField

    else:
        raise ResourceDefError(f"Unable to resolve field for type {type_}")


def is_optional(type_: Union) -> bool:
    """
    Field is an optional type
    """
    args = type_.__args__
    return (
        len(args) == 2 and type(None) in args
    )  # pylint: disable=unidiomatic-typecheck


def _resolve_list_from_sub_scripted_type(args: Sequence[Any], options: Options):
    """
    Handle the various types of sequence type
    """
    options.field_args["default"] = list

    (field,) = args
    if issubclass(field, ResourceBase):
        options.field_args["resource"] = field
        options.field_type = ListOf
    else:
        options.field_args["field"] = process_attribute(field)
        options.field_type = TypedListField


def _resolve_dict_from_sub_scripted_type(args: Sequence[Any], options: Options):
    """
    Handle the various types of sequence type
    """
    options.field_args["default"] = dict

    key_field, value_field = args
    # Use get origin to determine value is also sub-scripted. This is
    # required as issubclass cannot be used on sub-scripted fields.
    origin = get_origin(value_field)
    if not origin and issubclass(value_field, ResourceBase):
        options.field_args["resource"] = value_field
        options.field_type = DictOf

    else:
        options.field_args["key_field"] = process_attribute(key_field)
        options.field_args["value_field"] = process_attribute(value_field)
        options.field_type = TypedDictField


def _resolve_field_from_sub_scripted_type(origin: Type, options: Options, type_):
    """
    Resolve a field from a generic type
    """
    args = type_.__args__

    if origin is Union:
        if is_optional(type_):
            options.field_args["null"] = True
            _resolve_field_from_annotation(options, args[0])
        else:
            raise ResourceDefError(
                f"Unable to resolve field for sub-scripted type {type_}"
            )

    elif issubclass(origin, List):
        _resolve_list_from_sub_scripted_type(args, options)

    elif issubclass(origin, Dict):
        _resolve_dict_from_sub_scripted_type(args, options)

    else:
        raise ResourceDefError(f"Unable to resolve field for sub-scripted type {type_}")


def _resolve_field_from_annotation(options: Options, type_):
    """
    Resolve a field from a type annotation

    Handles generics, sequences and optional types
    """
    # Is a sub-scripted type
    if origin := get_origin(type_):
        _resolve_field_from_sub_scripted_type(origin, options, type_)

    # Is a basic type
    elif isinstance(type_, type):
        _resolve_field_from_type(options, type_)

    else:
        raise ResourceDefError(f"Annotation is not a type instance {type_}")


def process_attribute(
    type_: Type,
    value: Union[Options, Any] = NotProvided,
    *,
    _base_field: Type[BaseField] = BaseField,
) -> BaseField:
    """
    Process an individual attribute and generate a field based off values passed
    """

    # Attribute is already a field object
    if isinstance(value, _base_field):
        return value

    # Value is a default, wrap with Options
    if not isinstance(value, Options):
        value = Options(value)

    # Resolve field type from annotation
    if not value.field_type:
        _resolve_field_from_annotation(value, type_)

    # Finally instantiate a field object
    return value.init_field()
