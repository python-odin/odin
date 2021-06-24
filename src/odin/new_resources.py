from typing import Union, Any, Sequence, Callable, Dict, Tuple

from odin import NotProvided
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


class NewResourceType(type):
    def __new__(mcs, name, bases, attrs, meta_options=ResourceOptions):
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
        module = attrs.pop("__module__")
        new_class = super_new(mcs, name, bases, {"__module__": module})
        attr_meta = attrs.pop("Meta", None)
        abstract = getattr(attr_meta, "abstract", False)
        if not attr_meta:
            meta = getattr(new_class, "Meta", None)
        else:
            meta = attr_meta
        base_meta = getattr(new_class, "_meta", None)

        return new_class


class NewResource(
    ResourceBase, metaclass=NewResourceType, meta_options=ResourceOptions
):
    pass
