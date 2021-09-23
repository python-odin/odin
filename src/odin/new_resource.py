"""
New Style Resources
~~~~~~~~~~~~~~~~~~~

New style resources make use of Python type annotations to simplify the
definition of data structures.

New style resources still utilise many of the existing classes eg
``ResourceBase``, ``ResourceOptions`` and all existing fields. Allowing
existing code (eg Mappings, Codecs) including custom implementations to be
utilised unchanged.

Example:

.. code-block:: python



"""
import datetime
import decimal
import uuid
from pathlib import Path
from typing import Union, Any, Sequence, Callable, Dict, Tuple, Type, Optional, Mapping

import odin
from odin import NotProvided, registration
from odin.fields import Field, BaseField
from odin.resources import ResourceBase, ResourceOptions

__all__ = (
    "Validator",
    "Choices",
    "Options",
    "NewResourceType",
    "NewResource",
    "AbstractResource",
)

Validator = Callable[[Any], None]
Choices = Union[
    Sequence[Any], Sequence[Tuple[str, Any]], Sequence[Tuple[str, Any, str]],
]


class Options:
    """
    Define options to a field
    """

    __slots__ = (
        "field_type",
        "base_args",
        "field_args",
        "extra_args",
    )

    def __init__(
        self,
        default: Any = NotProvided,
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
        field_type: Type[BaseField] = None,
        **extra_args: Any
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
        final_args = self.base_args
        if issubclass(self.field_type, Field):
            final_args.update(self.field_args)
        return final_args

    def init_field(self):
        """
        Initialise field
        """
        if self.field_type:
            return self.field_type(**self._kwargs())
        # raise ResourceDefError("Field type could not be resolved")


def _new_meta_instance(meta_options_type, meta_def, new_class):
    """
    Generate meta options instance
    """
    new_meta = meta_options_type(meta_def)
    new_class.add_to_class("_meta", new_meta)

    base_meta = getattr(new_class, "_meta", None)

    # Namespace is inherited
    if base_meta and new_meta.name_space is NotProvided:
        new_meta.name_space = base_meta.name_space

    # Generate a namespace if one is not provided
    if new_meta.name_space is NotProvided:
        new_meta.name_space = new_class.__module__

    # Key field is inherited
    if base_meta and new_meta.key_field_names is None:
        new_meta.key_field_names = base_meta.key_field_names

    # Field sorting is inherited
    if new_meta.field_sorting is NotProvided:
        new_meta.field_sorting = base_meta.field_sorting if base_meta else False

    return new_meta


SIMPLE_TYPE_MAP = {
    bool: odin.BooleanField,
    datetime.date: odin.DateField,
    datetime.datetime: odin.DateTimeField,
    dict: odin.DictField,
    float: odin.FloatField,
    int: odin.IntegerField,
    list: odin.ListField,
    str: odin.StringField,
    datetime.time: odin.TimeField,
    uuid.UUID: odin.UUIDField,
}


def _is_optional(type_):
    if (
        len(type_.__args__) == 2
        and type(None) in type_.__args__  # pylint: disable=unidiomatic-typecheck
    ):
        pass


def _resolve_field_from_type(type_):
    """
    Resolve a field from a basic type
    """
    return SIMPLE_TYPE_MAP.get(type_)


def _resolve_field_from_generic(options: Options, type_):
    """
    Resolve a field from a generic type
    """
    origin = getattr(type_, "__origin__")
    name = str(origin)
    if name == "typing.Union":
        if (
            len(type_.__args__) == 2
            and type(None) in type_.__args__  # pylint: disable=unidiomatic-typecheck
        ):
            options.field_args["null"] = True
            _resolve_field_from_annotation(options, type_.__args__[0])
            return

    elif issubclass(origin, Sequence):
        return

    elif issubclass(origin, Mapping):
        return

    else:
        type_ = _resolve_field_from_type(type_.__args__[0])

    raise Exception("Not supported")


def _resolve_field_from_annotation(options: Options, type_):
    """
    Resolve a field from a type annotation

    Handles generics, sequences and optional types
    """
    origin = getattr(type_, "__origin__", None)
    if origin is not None:
        _resolve_field_from_generic(options, type_)

    elif isinstance(type_, ResourceBase):
        options.field_args["resource"] = type_
        options.field_type = odin.DictAs

    elif isinstance(type_, type):
        options.field_type = _resolve_field_from_type(type_)

    else:
        raise Exception(f"Not a supported value {type_}")


def _process_attribute(type_: Type, value: Union[Options, Any]):
    """
    Process an individual attribute
    """

    if isinstance(value, BaseField):
        # Attribute is already a field object
        return value

    if not (type_ or isinstance(value, Options)):
        # Attribute is neither annotated or an Options object
        return value

    if not isinstance(value, Options):
        # Create a options object from the value
        value = Options(value)

    if not value.field_type:
        # Resolve field type from annotation
        _resolve_field_from_annotation(value, type_)

    # Finally instantiate a field object
    return value.init_field()


def _iterate_attrs(attrs: Dict[str, Any]):
    annotations = attrs.pop("__annotations__", None) or {}

    for idx, (name, type_) in enumerate(annotations.items()):
        value = attrs.pop(name, NotProvided)
        yield name, _process_attribute(type_, value)


class NewResourceType(type):
    def __new__(
        mcs,
        name: str,
        bases,
        attrs: dict,
        meta_options_type: Type = ResourceOptions,
        abstract: bool = False,
    ):
        super_new = super().__new__

        # attrs will never be empty for classes declared in the standard way
        # (ie. with the `class` keyword). This is quite robust.
        if name == "NewBase" and attrs == {}:
            return super_new(mcs, name, bases, attrs)

        parents = [
            b
            for b in bases
            if isinstance(b, NewResourceType)
            and not (b.__name__ == "NewBase" and b.__mro__ == (b, object))
        ]
        if not parents:
            # If this isn't a subclass of NewResource, don't do anything special.
            return super_new(mcs, name, bases, attrs)

        # Create the class.
        new_class = super_new(mcs, name, bases, {"__module__": attrs.pop("__module__")})

        # Create new meta
        new_meta = _new_meta_instance(
            meta_options_type, attrs.pop("Meta", None), new_class
        )

        # Bail out early if we have already created this class.
        r = registration.get_resource(new_meta.resource_name)
        if r is not None:
            return r

        # Add all field attributes to the class.
        for name, field in _iterate_attrs(attrs):
            new_class.add_to_class(name, field)

        # Give fields an opportunity to do additional operations after the
        # resource is full populated and ready.
        for field in new_meta.all_fields:
            if hasattr(field, "on_resource_ready"):
                field.on_resource_ready()

        if abstract:
            return new_class

        # Register resource
        registration.register_resources(new_class)

        # Because of the way imports happen (recursively), we may or may not be
        # the first time this model tries to register with the framework. There
        # should only be one class for each model, so we always return the
        # registered version.
        return registration.get_resource(new_meta.resource_name)

    def add_to_class(cls, name, value):
        if hasattr(value, "contribute_to_class"):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)


class NewResource(
    ResourceBase, metaclass=NewResourceType, meta_options_type=ResourceOptions
):
    """
    New Style Resource utilising type annotations for defining fields
    """


class AbstractResource(
    ResourceBase,
    metaclass=NewResourceType,
    meta_options_type=ResourceOptions,
    abstract=True,
):
    """
    New Style Abstract Resource utilising type annotations for defining fields
    """
