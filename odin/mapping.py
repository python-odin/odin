# -*- coding: utf-8 -*-
import six
from odin.resources import Resource

__all__ = ('Mapping', 'map_field')

META_OPTION_NAMES = ()


class MappingOptions(object):
    pass


class MappingBase(type):
    """
    Metaclass for all Mappings
    """
    def __new__(cls, name, bases, attrs):
        super_new = super(MappingBase, cls).__new__

        # attrs will never be empty for classes declared in the standard way
        # (ie. with the `class` keyword). This is quite robust.
        if name == 'NewBase' and attrs == {}:
            return super_new(cls, name, bases, attrs)

        parents = [b for b in bases if isinstance(b, MappingBase) and not (b.__name__ == 'NewBase'
                                                                           and b.__mro__ == (b, object))]
        if not parents:
            # If this isn't a subclass of Mapping, don't do anything special.
            return super_new(cls, name, bases, attrs)

        from_resource = attrs.get('from_resource')
        if not issubclass(from_resource, Resource):
            raise ValueError('`from_resource` is not a Resource type')

        to_resource = attrs.get('to_resource')
        if not issubclass(to_resource, Resource):
            raise ValueError('`to_resource` is not a Resource type')

        exclude_fields = attrs.get('exclude_fields') or tuple()
        mappings = attrs.pop('mappings') or []

        from_fields = from_resource._meta.field_map




        field_mappings = []
        unmapped_fields = [f.attname for f in from_resource._meta.fields if f.attname not in exclude_fields]

        # Add simple custom mappings
        for mapping in mappings:
            from_fields, action, to_fields = mapping

        for from_field in from_resource._meta.fields:
            if from_field.attname in exclude_fields:
                continue

        return super_new(cls, name, bases, attrs)


class Mapping(six.with_metaclass(MappingBase)):
    from_resource = None
    to_resource = None
    exclude_fields = []
    mappings = []

    def __init__(self, source):
        self.source = source

    def convert(self):
        return self.to_resource()


def map_field(from_field, to_field):
    """
    Field decorator for custom mappings
    :param from_field:
    :param to_field:
    :return:
    """

    def inner(func):
        func.from_field = from_field
        func.to_field = to_field
        return func
    return inner
