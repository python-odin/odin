# -*- coding: utf-8 -*-
import six
from odin import registration
from odin.exceptions import MappingSetupError, MappingExecutionError
from odin.resources import Resource

__all__ = ('Mapping', 'map_field')


force_tuple = lambda x: x if isinstance(x, tuple) else (x,)


class MappingBase(type):
    """
    Meta-class for all Mappings
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
        if not (isinstance(from_resource, type) and issubclass(from_resource, Resource)):
            raise MappingSetupError('`from_resource` is not a Resource type')

        to_resource = attrs.get('to_resource')
        if not (isinstance(to_resource, type) and issubclass(to_resource, Resource)):
            raise MappingSetupError('`to_resource` is not a Resource type')

        # Check if we have already created this mapping
        try:
            return registration.get_mapping(from_resource, to_resource)
        except KeyError:
            pass  # Not registered

        # Generate mapping rules.
        from_fields = from_resource._meta.field_map
        to_fields = to_resource._meta.field_map

        def attr_mapping_to_mapping_rule(m, def_type, ref):
            """
            Parse mapping attributes and force to from_fields, action, to_fields tuple.
            """
            try:
                map_from, action, map_to = m
            except ValueError:
                raise MappingSetupError('Bad mapping definition `%s` in %s `%s`.' % (m, def_type, ref))

            map_from = force_tuple(map_from)
            for f in map_from:
                if not f in from_fields:
                    raise MappingSetupError('Field `%s` of %s `%s` not found on from resource. ' % (f, def_type, ref))

            if isinstance(action, six.string_types):
                if action not in attrs:
                    raise MappingSetupError('Action named %s defined in %s `%s` was not defined on mapping object.' % (action, def_type, ref))
                if not callable(attrs[action]):
                    raise MappingSetupError('Action named %s defined in %s `%s` is not callable.' % (action, def_type, ref))
            elif action is not None and not callable(action):
                raise MappingSetupError('Action on %s `%s` is not callable.' % (def_type, ref))

            map_to = force_tuple(map_to)
            for f in map_to:
                if not f in to_fields:
                    raise MappingSetupError('Field `%s` of %s `%s` not found on to resource. ' % (f, def_type, ref))

            return map_from, action, map_to

        exclude_fields = attrs.get('exclude_fields') or tuple()
        unmapped_fields = [attname for attname in from_fields if attname not in exclude_fields]
        mapping_rules = []

        # Add basic mappings
        for idx, mapping in enumerate(attrs.pop('mappings', [])):
            map_from, action, map_to = attr_mapping_to_mapping_rule(mapping, 'basic mapping', idx)
            mapping_rules.append((map_from, action, map_to))
            if len(map_from) == 1 and map_from[0] in unmapped_fields:
                unmapped_fields.remove(map_from[0])
            if len(map_to) == 1 and map_to[0] in unmapped_fields:
                unmapped_fields.remove(map_to[0])

        # Add custom mappings
        for attr in attrs.values():
            if hasattr(attr, '_mapping'):
                map_from, action, map_to = attr_mapping_to_mapping_rule(attr._mapping, 'custom mapping', attr)
                mapping_rules.append((map_from, action, map_to))
                if len(map_from) == 1 and map_from[0] in unmapped_fields:
                    unmapped_fields.remove(map_from[0])
                if len(map_to) == 1 and map_to[0] in unmapped_fields:
                    unmapped_fields.remove(map_to[0])

                delattr(attr, '_mapping')

        # Add auto mapped fields
        for field in unmapped_fields:
            if field in to_fields:
                mapping_rules.append(((field,), None, (field,)))

        # Update mappings
        attrs['_mapping_rules'] = mapping_rules

        registration.register_mappings(super_new(cls, name, bases, attrs))
        return registration.get_mapping(from_resource, to_resource)


class Mapping(six.with_metaclass(MappingBase)):
    from_resource = None
    to_resource = None
    exclude_fields = []
    mappings = []

    def __init__(self, source):
        if not isinstance(source, self.from_resource):
            raise TypeError('Source parameter must be an instance of %s' % self.from_resource)
        self.source = source

    def _apply_rule(self, mapping_rule):
        from_fields, action, to_fields = mapping_rule

        from_values = tuple(getattr(self.source, f) for f in from_fields)

        if action is None:
            to_values = from_values
        else:
            if isinstance(action, six.string_types):
                action = getattr(self, action)
            try:
                to_values = action(*from_values)
            except TypeError as ex:
                raise MappingExecutionError('%s applying rule %s' % (ex, mapping_rule))
            else:
                to_values = force_tuple(to_values)

        if len(to_fields) != len(to_values):
            raise MappingExecutionError('Rule expects %s arguments (%s received) applying rule %s' % (
                len(to_fields), len(to_values), mapping_rule))

        return {f: to_values[i] for i, f in enumerate(to_fields)}

    def convert(self, **field_values):
        """
        Convert the provided source into a target resource.
        """
        values = field_values

        for mapping_rule in self._mapping_rules:
            values.update(self._apply_rule(mapping_rule))

        return self.to_resource(**values)


def map_field(from_field=None, to_field=None):
    """
    Field decorator for custom mappings
    :param from_field:
    :param to_field:
    :return:
    """
    def inner(func):
        from_ = from_field or func.__name__
        to_ = to_field or from_
        func._mapping = (from_, func.__name__, to_)
        return func
    return inner
