"""Composite fields for handling collections of resources."""
import abc
from functools import cached_property
from typing import Any, Callable, Iterator, Tuple

from odin import bases, exceptions
from odin.fields import Field
from odin.resources import create_resource_from_dict
from odin.utils import value_in_choices
from odin.validators import EMPTY_VALUES

__all__ = (
    "CompositeField",
    "DictAs",
    "ObjectAs",
    "ListOf",
    "ArrayOf",
    "DictOf",
)


class CompositeField(Field, metaclass=abc.ABCMeta):
    """The base class for composite.

    Fields that contain other resources eg DictAs/ListOf fields."""

    @classmethod
    def delayed(cls, resource_callable: Callable[[], Any], **options):
        """Create a delayed resource field.

        This is used in the case of tree structures where a resource may reference itself.

        This should be used with a lambda function to avoid referencing an incomplete type.

        .. code-block:: python

            class Category(odin.Resource):
                name = odin.StringField()
                child_categories = odin.DictAs.delayed(lambda: Category)

        """
        return cls(resource_callable, **options)

    def __init__(self, resource, use_container=False, **options):
        """Initialisation of a CompositeField.

        :param resource:
        :param use_container: Special flag for codecs that support containers or just multiple instances of a
            sub element (ie XML).
        :param empty: This collection can be empty
        :param options: Additional options passed to :py:class:`odin.fields.Field` super class.

        """

        if not hasattr(resource, "_meta"):
            if callable(resource):
                # Delayed resolution of the resource type.
                self._of = resource
            else:
                # Keep this pattern so old behaviour remains.
                raise TypeError(
                    f"{resource!r} is not a valid type for a related field."
                )
        else:
            self._of = resource
        self.use_container = use_container

        if not options.get("null", False):
            options.setdefault("default", lambda: self.of())

        super().__init__(**options)

    @cached_property
    def of(self):
        """Return the resource type."""
        resource = self._of
        if not hasattr(resource, "_meta") and callable(resource):
            resource = resource()
            if not hasattr(resource, "_meta"):
                raise TypeError(
                    f"{resource!r} is not a valid type for a related field."
                )
        return resource

    def to_python(self, value):
        """Convert raw value to a python value."""
        if value is None:
            return None
        if isinstance(value, self.of):
            return value
        if isinstance(value, dict):
            return create_resource_from_dict(value, self.of, full_clean=False)
        msg = self.error_messages["invalid"] % self.of
        raise exceptions.ValidationError(msg)

    def validate(self, value):
        """Validate the value."""
        super().validate(value)
        if value not in EMPTY_VALUES:
            value.full_clean()

    @abc.abstractmethod
    def item_iter_from_object(self, obj):
        """Return an iterator of items (resource, idx) from composite field.

        For single items (eg ``DictAs`` will return a list a single item (resource, None))
        """

    @abc.abstractmethod
    def key_to_python(self, key):
        """A to python method for the key value."""


class DictAs(CompositeField):
    """Treat a dictionary as a Resource."""

    default_error_messages = {
        "invalid": "Must be a dict of type ``%r``.",
    }
    data_type_name = "Dict as"

    def item_iter_from_object(self, obj):
        resource = self.value_from_object(obj)
        if resource:
            yield (None, resource)

    def key_to_python(self, key):
        pass  # Not required as keys are not used.


ObjectAs = DictAs


class ListOf(CompositeField):
    """List of resources."""

    default_error_messages = {
        "invalid": "Must be a list of ``%r`` objects.",
        "null": "List cannot contain null entries.",
        "empty": "List cannot be empty",
    }
    data_type_name = "List of"

    def __init__(self, resource, empty=True, **options):
        """Initialisation of a ListOf field."""
        options.setdefault("default", list)
        super().__init__(resource, **options)
        self.empty = empty

    @staticmethod
    def _process_list(value_list, method):
        values = []
        errors = {}
        for idx, value in enumerate(value_list):
            error_key = str(idx)

            try:
                values.append(method(value))
            except exceptions.ValidationError as ve:
                errors[error_key] = ve.error_messages

        if errors:
            raise exceptions.ValidationError(errors)

        return values

    def to_python(self, value):
        """Convert raw value to a python value."""
        if value is None:
            return None
        if isinstance(value, (list, bases.ResourceIterable)):
            super_to_python = super().to_python

            def process(val):
                if val is None:
                    raise exceptions.ValidationError(self.error_messages["null"])
                return super_to_python(val)

            return self._process_list(value, process)
        msg = self.error_messages["invalid"] % self.of
        raise exceptions.ValidationError(msg)

    def validate(self, value):
        """Validate the value."""
        # Skip The direct super method and apply it to each list item.
        super(CompositeField, self).validate(value)  # noqa
        if value is not None:
            super_validate = super().validate
            self._process_list(value, super_validate)

        if (value is not None) and (not value) and (not self.empty):
            raise exceptions.ValidationError(self.error_messages["empty"])

    def __iter__(self):
        # This does nothing, but it does prevent inspections from complaining.
        return None  # NoQA

    def item_iter_from_object(self, obj):
        resources = self.value_from_object(obj)
        if resources:
            yield from enumerate(resources)

    def key_to_python(self, key):
        """A to python method for the key value."""
        return int(key)


ArrayOf = ListOf


class DictOf(CompositeField):
    """Dictionary of resources."""

    default_error_messages = {
        "invalid": "Must be a dict of ``%r`` objects.",
        "null": "Dict cannot contain null entries.",
        "empty": "List cannot be empty",
        "invalid_key": "Key %r is not a valid choice.",
    }
    data_type_name = "Dict of"

    def __init__(self, resource, empty=True, key_choices=None, **options):
        """Initialise DictOf field."""
        options.setdefault("default", dict)
        super().__init__(resource, **options)
        self.empty = empty
        self.key_choices = key_choices

    def _process_dict(self, value_dict, method):
        values = {}
        errors = {}
        key_choices = self.key_choices
        for key, value in value_dict.items():
            if key_choices and not value_in_choices(key, key_choices):
                msg = self.error_messages["invalid_key"] % value
                raise exceptions.ValidationError(msg)

            try:
                values[key] = method(value)
            except exceptions.ValidationError as ve:
                errors[key] = ve.error_messages

        if errors:
            raise exceptions.ValidationError(errors)

        return values

    def to_python(self, value):
        """Convert raw value to a python type."""
        if value is None:
            return None
        if isinstance(value, dict):
            super_to_python = super().to_python

            def process(val):
                if val is None:
                    raise exceptions.ValidationError(
                        self.error_messages["null"], code="null"
                    )
                return super_to_python(val)

            return self._process_dict(value, process)
        msg = self.error_messages["invalid"] % self.of
        raise exceptions.ValidationError(msg)

    def validate(self, value):
        """Validate the value."""
        # Skip The direct super method and apply it to each list item.
        super(CompositeField, self).validate(value)  # noqa
        if value is not None:
            super_validate = super().validate
            self._process_dict(value, super_validate)

        if (value is not None) and (not value) and (not self.empty):
            raise exceptions.ValidationError(self.error_messages["empty"], code="empty")

    def __iter__(self):
        # This does nothing, it does prevent inspections from complaining.
        return None  # NoQA

    def item_iter_from_object(self, obj) -> Iterator[Tuple[str, Any]]:
        """Iterate object returning key/value pairs"""
        resources = self.value_from_object(obj)
        if resources:
            for key in sorted(resources):
                yield key, resources[key]

    def key_to_python(self, key):
        """A to python method for the key value."""
        return key
