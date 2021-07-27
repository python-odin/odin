from typing import Union, Any, Sequence, Callable, Dict, Tuple, Type

from odin import NotProvided, registration
from odin.resources import ResourceBase, ResourceOptions

Validator = Callable[[Any], None]
Choices = Union[
    Sequence[Any], Sequence[Tuple[str, Any]], Sequence[Tuple[str, Any, str]],
]


class Options:
    """
    Define options to a field
    """

    __slots__ = (
        "default",
        "name",
        "verbose_name",
        "verbose_name_plural",
        "validators",
        "choices",
        "use_default_if_not_provided",
        "error_messages",
        "doc_text",
        "is_attribute",
        "key",
    )

    def __init__(
        self,
        default: Any = NotProvided,
        *,
        name: str = None,
        verbose_name: str = None,
        verbose_name_plural: str = None,
        validators: Sequence[Validator] = None,
        choices: Choices = None,
        use_default_if_not_provided: bool = True,
        error_messages: Dict[str, str] = None,
        doc_text: str = "",
        is_attribute: bool = False,
        key: bool = False
    ):
        self.default = default
        self.name = name
        self.verbose_name = verbose_name
        self.verbose_name_plural = verbose_name_plural
        self.validators = validators
        self.choices = choices
        self.use_default_if_not_provided = use_default_if_not_provided
        self.error_messages = error_messages
        self.doc_text = doc_text
        self.is_attribute = is_attribute
        self.key = key


def _new_meta_instance(meta_options_type, meta_def, new_class):
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


def _iterate_fields(attrs):
    pass


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

        # Determine and add fields

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
    pass


class AbstractResource(
    ResourceBase,
    metaclass=NewResourceType,
    meta_options_type=ResourceOptions,
    abstract=True,
):
    pass
