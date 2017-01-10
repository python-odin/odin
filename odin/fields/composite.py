# -*- coding: utf-8 -*-
import six
from odin import bases
from odin import exceptions
from odin.resources import create_resource_from_dict
from odin.fields import Field
from odin.utils import value_in_choices
from odin.validators import EMPTY_VALUES

__all__ = ('CompositeField', 'DictAs', 'ObjectAs', 'ListOf', 'ArrayOf', 'DictOf')


class CompositeField(Field):
    """
    The base class for composite (or fields that contain other resources) eg DictAs/ListOf fields.
    """
    def __init__(self, resource, use_container=False, **options):
        """
        Initialisation of a CompositeField.

        :param resource:
        :param use_container: Special flag for codecs that support containers or just multiple instances of a
            sub element (ie XML).
        :param empty: This collection can be empty
        :param options: Additional options passed to :py:class:`odin.fields.Field` super class.

        """
        try:
            resource._meta
        except AttributeError:
            raise TypeError("``%r`` is not a valid type for a related field." % resource)
        self.of = resource
        self.use_container = use_container

        if not options.get('null', False):
            options.setdefault('default', lambda: resource())

        super(CompositeField, self).__init__(**options)

    def to_python(self, value):
        if value is None:
            return None
        if isinstance(value, self.of):
            return value
        if isinstance(value, dict):
            return create_resource_from_dict(value, self.of._meta.resource_name)
        msg = self.error_messages['invalid'] % self.of
        raise exceptions.ValidationError(msg)

    def validate(self, value):
        super(CompositeField, self).validate(value)
        if value not in EMPTY_VALUES:
            value.full_clean()

    def item_iter_from_object(self, obj):
        """
        Return an iterator of items (resource, idx) from composite field.

        For single items (eg ``DictAs`` will return a list a single item (resource, None))

        :param obj:
        :return:
        """
        raise NotImplementedError()

    def key_to_python(self, key):
        """
        A to python method for the key value.
        :param key:
        :return:
        """
        raise NotImplementedError()


class DictAs(CompositeField):
    """
    Treat a dictionary as a Resource.
    """
    default_error_messages = {
        'invalid': "Must be a dict of type ``%r``.",
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
    """
    List of resources.
    """
    default_error_messages = {
        'invalid': "Must be a list of ``%r`` objects.",
        'null': "List cannot contain null entries.",
        'empty': "List cannot be empty",
    }
    data_type_name = "List of"

    def __init__(self, resource, empty=True, **options):
        options.setdefault('default', list)
        super(ListOf, self).__init__(resource, **options)
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
        if value is None:
            return None
        if isinstance(value, (list, bases.ResourceIterable)):
            super_to_python = super(ListOf, self).to_python

            def process(val):
                if val is None:
                    raise exceptions.ValidationError(self.error_messages['null'])
                return super_to_python(val)

            return self._process_list(value, process)
        msg = self.error_messages['invalid'] % self.of
        raise exceptions.ValidationError(msg)

    def validate(self, value):
        # Skip The direct super method and apply it to each list item.
        super(CompositeField, self).validate(value)  # noqa
        if value is not None:
            super_validate = super(ListOf, self).validate
            self._process_list(value, super_validate)

        if (value is not None) and (not value) and (not self.empty):
            raise exceptions.ValidationError(self.error_messages['empty'])

    def __iter__(self):
        # This does nothing but it does prevent inspections from complaining.
        return None  # NoQA

    def item_iter_from_object(self, obj):
        resources = self.value_from_object(obj)
        if resources:
            for i in enumerate(resources):
                yield i

    def key_to_python(self, key):
        """
        A to python method for the key value.
        :param key:
        :return:
        """
        return int(key)

ArrayOf = ListOf


class DictOf(CompositeField):
    """
    Dictionary of resources.
    """
    default_error_messages = {
        'invalid': "Must be a dict of ``%r`` objects.",
        'null': "Dict cannot contain null entries.",
        'empty': "List cannot be empty",
        'invalid_key': 'Key %r is not a valid choice.',
    }
    data_type_name = "Dict of"

    def __init__(self, resource, empty=True, key_choices=None, **options):
        options.setdefault('default', dict)
        super(DictOf, self).__init__(resource, **options)
        self.empty = empty
        self.key_choices = key_choices

    def _process_dict(self, value_dict, method):
        values = {}
        errors = {}
        key_choices = self.key_choices
        for key, value in six.iteritems(value_dict):
            if key_choices and not value_in_choices(key, key_choices):
                msg = self.error_messages['invalid_key'] % value
                raise exceptions.ValidationError(msg)

            try:
                values[key] = method(value)
            except exceptions.ValidationError as ve:
                errors[key] = ve.error_messages

        if errors:
            raise exceptions.ValidationError(errors)

        return values

    def to_python(self, value):
        if value is None:
            return None
        if isinstance(value, dict):
            super_to_python = super(DictOf, self).to_python

            def process(val):
                if val is None:
                    raise exceptions.ValidationError(self.error_messages['null'], code='null')
                return super_to_python(val)

            return self._process_dict(value, process)
        msg = self.error_messages['invalid'] % self.of
        raise exceptions.ValidationError(msg)

    def validate(self, value):
        # Skip The direct super method and apply it to each list item.
        super(CompositeField, self).validate(value)  # noqa
        if value is not None:
            super_validate = super(DictOf, self).validate
            self._process_dict(value, super_validate)

        if (value is not None) and (not value) and (not self.empty):
            raise exceptions.ValidationError(self.error_messages['empty'], code='empty')

    def __iter__(self):
        # This does nothing but it does prevent inspections from complaining.
        return None  # NoQA

    def item_iter_from_object(self, obj):
        resources = self.value_from_object(obj)
        if resources:
            for key in sorted(resources):
                yield key, resources[key]

    def key_to_python(self, key):
        """
        A to python method for the key value.
        :param key:
        :return:
        """
        return key
