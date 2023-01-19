from typing import Any, Callable, Union, Sequence

from odin.utils import force_tuple, getmeta

from .base import BaseField

__all__ = (
    "ConstantField",
    "CalculatedField",
    "calculated_field",
    "MultiPartField",
)


class VirtualField(BaseField):
    """
    Base class for virtual fields. A virtual fields is treated like any other field during encoding/decoding (provided
    it can be written to).
    """

    data_type_name = None

    def __init__(
        self,
        verbose_name: str = None,
        verbose_name_plural: str = None,
        name: str = None,
        data_type_name: str = None,
        doc_text: str = "",
        is_attribute: bool = False,
        key: bool = False,
    ):
        """
        Initialisation of virtual field

        :param verbose_name: Display name of field.
        :param verbose_name_plural: Plural display name of field.
        :param name: Name of the serialised field.
        :param data_type_name: A name for the data type this field returns (used for generating documentation)
        :param doc_text: Documentation for the field, replaces help text
        :param is_attribute: Special flag for codecs that support attributes on nodes (ie XML)
        """
        super().__init__(verbose_name, verbose_name_plural, name, doc_text)

        self.data_type_name = data_type_name
        self.is_attribute = is_attribute
        self.key = key

        self.resource = None

    def __get__(self, instance, owner):
        raise NotImplementedError

    def __set__(self, instance, value):
        raise AttributeError("Read only")

    def contribute_to_class(self, cls, name):
        self.set_attributes_from_name(name)
        self.resource = cls
        getmeta(cls).add_virtual_field(self)
        setattr(cls, name, self)


class ConstantField(VirtualField):
    """
    A field that provides a constant value.
    """

    __slots__ = ("value",)

    def __init__(self, value: Any, **kwargs):
        super().__init__(**kwargs)
        self.value = value

    def __get__(self, instance, owner):
        return self.value


class CalculatedField(VirtualField):
    """
    A field whose value is calculated by an expression.

    The expression should accept a single "self" parameter that is a Resource instance.
    """

    __slots__ = ("expr",)

    def __init__(self, expr: Callable[[Any], Any], **kwargs):
        super().__init__(**kwargs)
        self.expr = expr

    def __get__(self, instance, owner):
        return self.expr(instance)


def calculated_field(method=None, **kwargs):
    """
    Decorator that converts an instance method into a calculated field.
    """

    def inner(expr):
        if method.__doc__ is not None:
            doc_text = method.__doc__.strip()
            if doc_text:
                kwargs.setdefault("doc_text", doc_text)
        return CalculatedField(expr, **kwargs)

    return inner if method is None else inner(method)


class MultiPartField(VirtualField):
    """
    A field whose value is the combination of several other fields.

    This field should be included after the field that make up the multipart value.
    """

    __slots__ = ("field_names", "separator", "_fields")

    def __init__(
        self, field_names: Union[str, Sequence[str]], separator: str = "", **kwargs
    ):
        """
        :param field_names: Name(s) of fields to make up key
        :param separator: Separator to use between values.
        :param kwargs: Additional kwargs for VirtualField

        """
        kwargs.setdefault("data_type_name", "String")
        super().__init__(**kwargs)
        self.field_names = force_tuple(field_names)
        self.separator = separator
        self._fields = None

    def __get__(self, instance, owner):
        return self.generate_value(instance)

    def generate_value(self, instance):
        """
        Generate a key based on other values.
        """
        values = [f.prepare(f.value_from_object(instance)) for f in self._fields]
        return self.separator.join(str(v) for v in values)

    def on_resource_ready(self):
        # Extract reference to fields
        meta = getmeta(self.resource)
        try:
            self._fields = tuple(meta.field_map[name] for name in self.field_names)
        except KeyError as ex:
            raise AttributeError(f"Attribute {ex} not found on {self.resource!r}")
