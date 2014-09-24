# -*- coding: utf-8 -*-
import six
from odin import exceptions
from odin.resources import create_resource_from_dict
from odin.fields import Field
from odin.validators import EMPTY_VALUES

__all__ = ('CompositeField', 'DictAs', 'ObjectAs', 'ListOf', 'ArrayOf', 'DictOf')


class CompositeField(Field):
    """
    The base class for composite (or fields that contain other resources) eg DictAs/ListOf fields.
    """
    def __init__(self, resource, **options):
        try:
            resource._meta
        except AttributeError:
            raise TypeError("``%r`` is not a valid type for a related field." % resource)
        self.of = resource

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
        raise NotImplementedError

    def key_to_python(self, key):
        """
        A to python method for the key value.
        :param key:
        :return:
        """
        raise NotImplementedError()


class DictAs(CompositeField):
    default_error_messages = {
        'invalid': "Must be a dict of type ``%r``.",
    }
    data_type_name = "Dict as"

    def item_iter_from_object(self, obj):
        resource = self.value_from_object(obj)
        if resource:
            yield (None, resource)

ObjectAs = DictAs


class ListOf(CompositeField):
    default_error_messages = {
        'invalid': "Must be a list of ``%r`` objects.",
        'null': "List cannot contain null entries.",
    }
    data_type_name = "List of"

    def __init__(self, resource, **options):
        options.setdefault('default', list)
        super(ListOf, self).__init__(resource, **options)

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
        if isinstance(value, list):
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
        super(CompositeField, self).validate(value)
        if value not in EMPTY_VALUES:
            super_validate = super(ListOf, self).validate
            self._process_list(value, super_validate)

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
    default_error_messages = {
        'invalid': "Must be a dict of ``%r`` objects.",
        'null': "Dict cannot contain null entries.",
    }
    data_type_name = "Dict of"

    def __init__(self, resource, **options):
        options.setdefault('default', dict)
        super(DictOf, self).__init__(resource, **options)

    @staticmethod
    def _process_dict(value_dict, method):
        values = {}
        errors = {}
        for key, value in six.iteritems(value_dict):
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
                    raise exceptions.ValidationError(self.error_messages['null'])
                return super_to_python(val)

            return self._process_dict(value, process)
        msg = self.error_messages['invalid'] % self.of
        raise exceptions.ValidationError(msg)

    def validate(self, value):
        # Skip The direct super method and apply it to each list item.
        super(CompositeField, self).validate(value)
        if value not in EMPTY_VALUES:
            super_validate = super(DictOf, self).validate
            self._process_dict(value, super_validate)

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
