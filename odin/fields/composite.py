# -*- coding: utf-8 -*-
import six
from odin import exceptions
from odin.resources import create_resource_from_dict
from odin.fields import Field
from odin.validators import EMPTY_VALUES

__all__ = ('DictAs', 'ObjectAs', 'ListOf', 'ArrayOf', 'DictOf')


class DictAs(Field):
    default_error_messages = {
        'invalid': "Must be a object of type ``%r``.",
    }

    def __init__(self, resource, **options):
        try:
            resource._meta
        except AttributeError:
            raise TypeError("``%r`` is not a valid type for a related field." % resource)
        self.of = resource

        options.setdefault('default', lambda: resource())
        super(DictAs, self).__init__(**options)

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
        super(DictAs, self).validate(value)
        if value not in EMPTY_VALUES:
            value.full_clean()

ObjectAs = DictAs


class ListOf(DictAs):
    default_error_messages = {
        'invalid': "Must be a list of ``%r`` objects.",
        'null': "List cannot contain null entries.",
    }

    def __init__(self, resource, **options):
        options.setdefault('default', list)
        super(ListOf, self).__init__(resource, **options)

    def _process_list(self, value_list, method):
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
        super(DictAs, self).validate(value)
        if value not in EMPTY_VALUES:
            super_validate = super(ListOf, self).validate
            self._process_list(value, super_validate)

    def __iter__(self):
        # This does nothing but it does prevent inspections from complaining.
        return None  # noqa

ArrayOf = ListOf


class DictOf(DictAs):
    default_error_messages = {
        'invalid': "Must be a dict of ``%r`` objects.",
        'null': "Dict cannot contain null entries.",
    }

    def __init__(self, resource, **options):
        options.setdefault('default', dict)
        super(DictOf, self).__init__(resource, **options)

    def _process_dict(self, value_dict, method):
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
        super(DictAs, self).validate(value)
        if value not in EMPTY_VALUES:
            super_validate = super(DictOf, self).validate
            self._process_dict(value, super_validate)

    def __iter__(self):
        # This does nothing but it does prevent inspections from complaining.
        return None  # noqa
