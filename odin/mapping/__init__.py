# -*- coding: utf-8 -*-
import collections
import six
from odin import registration
from odin.exceptions import MappingSetupError, MappingExecutionError
from odin.resources import Resource

__all__ = ('Mapping', 'map_field', 'map_list_field')


force_tuple = lambda x: x if isinstance(x, (list, tuple)) else (x,)


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
            # Parse, validate and normalise defined mapping rules so rules can be executed without having to
            # perform checks during a mapping operation.
            to_list = False
            try:
                map_from, action, map_to, to_list = m
            except ValueError:
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
                    raise MappingSetupError('Action named %s defined in %s `%s` was not defined on mapping object.' % (
                        action, def_type, ref))
                if not callable(attrs[action]):
                    raise MappingSetupError('Action named %s defined in %s `%s` is not callable.' % (
                        action, def_type, ref))
            elif action is not None and not callable(action):
                raise MappingSetupError('Action on %s `%s` is not callable.' % (def_type, ref))

            map_to = force_tuple(map_to)
            if to_list and len(map_to) != 1:
                raise MappingSetupError('The %s `%s` specifies a to_list mapping, these can only be applied to a '
                                        'single target field.' % (def_type, m))
            for f in map_to:
                if not f in to_fields:
                    raise MappingSetupError('Field `%s` of %s `%s` not found on to resource. ' % (f, def_type, ref))

            return map_from, action, map_to, to_list

        def remove_from_unmapped_fields(rule):
            # Remove any fields that are handled by a mapping rule from unmapped_fields list.
            map_from, _, map_to, _ = rule
            if len(map_from) == 1 and map_from[0] in unmapped_fields:
                unmapped_fields.remove(map_from[0])
            if len(map_to) == 1 and map_to[0] in unmapped_fields:
                unmapped_fields.remove(map_to[0])

        exclude_fields = attrs.get('exclude_fields') or tuple()
        unmapped_fields = [attname for attname in from_fields if attname not in exclude_fields]
        mapping_rules = []

        # Add basic mappings
        for idx, mapping in enumerate(attrs.pop('mappings', [])):
            mapping_rule = attr_mapping_to_mapping_rule(mapping, 'basic mapping', idx)
            mapping_rules.append(mapping_rule)
            remove_from_unmapped_fields(mapping_rule)

        # Add custom mappings
        for attr in attrs.values():
            # Methods with a _mapping attribute have been decorated by either `map_field` or `map_list_field`
            # decorators.
            if hasattr(attr, '_mapping'):
                mapping_rule = attr_mapping_to_mapping_rule(getattr(attr, '_mapping'), 'custom mapping', attr)
                mapping_rules.append(mapping_rule)
                remove_from_unmapped_fields(mapping_rule)
                # Remove mapping
                delattr(attr, '_mapping')

        # Add auto mapped fields that are yet to be mapped.
        for field in unmapped_fields:
            if field in to_fields:
                mapping_rules.append(((field,), None, (field,), False))

        # Update mappings
        attrs['_mapping_rules'] = mapping_rules

        registration.register_mappings(super_new(cls, name, bases, attrs))
        return registration.get_mapping(from_resource, to_resource)


class Mapping(six.with_metaclass(MappingBase)):
    from_resource = None
    to_resource = None
    exclude_fields = []
    mappings = []

    @classmethod
    def apply(cls, source_resource):
        """
        Apply conversion either a single resource or a list of resources using the mapping defined by this class.

        If a list of resources is supplied an iterable is returned.
        """
        if isinstance(source_resource, (list, tuple)):
            return (cls(s).convert() for s in source_resource)
        else:
            return cls(source_resource).convert()

    def __init__(self, source):
        if not isinstance(source, self.from_resource):
            raise TypeError('Source parameter must be an instance of %s' % self.from_resource)
        self.source = source

    def _apply_rule(self, mapping_rule):
        from_fields, action, to_fields, to_list = mapping_rule

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

        if to_list:
            if isinstance(to_values, collections.Iterable):
                to_values = (list(to_values),)
        else:
            to_values = force_tuple(to_values)

        if len(to_fields) != len(to_values):
            raise MappingExecutionError('Rule expects %s fields (%s received) applying rule %s' % (
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


def map_field(func=None, from_field=None, to_field=None, to_list=False):
    """
    Field decorator for custom mappings
    :param from_field:
    :param to_field:
    :return:
    """
    def inner(func):
        func._mapping = (
            from_field or func.__name__,
            func.__name__,
            to_field or func.__name__,
            to_list
        )
        return func

    return inner(func) if func else inner


def map_list_field(func=None, from_field=None, to_field=None):
    """
    Field decorator for custom mappings that return a single list.

    This mapper also allows for returning an iterator that will be converted
    into a list during the mapping operation.
    """
    return map_field(func, from_field, to_field, True)
