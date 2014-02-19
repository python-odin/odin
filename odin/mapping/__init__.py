# -*- coding: utf-8 -*-
import collections
import six
from odin import registration
from odin.resources import Resource
from odin.fields.composite import ListOf, DictAs
from odin.exceptions import MappingSetupError, MappingExecutionError
from odin.mapping.helpers import MapListOf, MapDictAs
from odin.utils import cached_property

__all__ = ('Mapping', 'map_field', 'map_list_field')


force_tuple = lambda x: x if isinstance(x, (list, tuple)) else (x,)


def define(from_field, action, to_field, to_list=False, bind=False, skip_if_none=False):
    """Helper method for defining a mapping.

    :param from_field: Source field to map from.
    :param action: Action to perform during mapping.
    :param to_field: Destination field to map to.
    :param to_list: Assume the result is a list (rather than a multi value tuple).
    :param bind: During the mapping operation the first parameter should be the mapping instance.
    :param skip_if_none: If the from field is :const:`None` do not include the field (this allows the destination
        object to define it's own supply defaults etc)
    :return: A mapping definition.
    """
    return force_tuple(from_field), action, force_tuple(to_field), to_list, bind, skip_if_none


class FieldResolverBase(object):
    """Base class for field resolver objects"""
    def __init__(self, obj):
        self.obj = obj

    def __iter__(self):
        return iter(self.field_dict)

    def __contains__(self, item):
        return item in self.field_dict

    def __getitem__(self, item):
        return self.field_dict[item]

    @cached_property
    def field_dict(self):
        """Property accessor for the attribute dict"""
        return self.get_field_dict()

    def get_field_dict(self):
        """ Return an field map consisting of an attribute and a Field object (if one is used).

        For resource objects the field object would be an Odin resource field, for Django models a model field etc. If
        you are building a generic object mapper the field object can be :const:`None`.

        The field object is used to determine certain automatic mapping operations (ie Lists of Odin resources to other
        Odin resources).

        :return: Dictionary
        """
        raise NotImplementedError()


class ResourceFieldResolver(FieldResolverBase):
    """Field resolver for Odin resource objects."""
    def get_field_dict(self):
        """Return a dictionary of fields along with their names."""
        return self.obj._meta.field_map

registration.register_field_resolver(ResourceFieldResolver, Resource)


def _generate_auto_mapping(name, from_fields, to_fields):
    """
    Generate the auto mapping between two fields.
    """
    from_field = from_fields[name]
    to_field = to_fields[name]

    # Handle ListOf fields
    if isinstance(from_field, ListOf) and isinstance(to_field, ListOf):
        try:
            mapping = registration.get_mapping(from_field.of, to_field.of)
            return define(name, MapListOf(mapping), name, to_list=True, bind=True)
        except KeyError:
            pass

    # Handle DictAs fields
    elif isinstance(from_field, DictAs) and isinstance(to_field, DictAs):
        try:
            mapping = registration.get_mapping(from_field.of, to_field.of)
            return define(name, MapDictAs(mapping), name, bind=True)
        except KeyError:
            pass

    return define(name, None, name)


class MappingMeta(type):
    """
    Meta-class for all Mappings
    """
    def __new__(cls, name, bases, attrs):
        super_new = super(MappingMeta, cls).__new__

        # attrs will never be empty for classes declared in the standard way
        # (ie. with the `class` keyword). This is quite robust.
        if name == 'NewBase' and attrs == {}:
            return super_new(cls, name, bases, attrs)

        parents = [b for b in bases if isinstance(b, MappingMeta) and not (b.__name__ == 'NewBase'
                                                                           and b.__mro__ == (b, MappingBase, object))]
        if not parents:
            # If this isn't a subclass of Mapping, don't do anything special.
            return super_new(cls, name, bases, attrs)

        from_obj = attrs.get('from_resource')
        if from_obj is None:
            raise MappingSetupError('`from_resource` is not defined.')
        to_obj = attrs.get('to_resource')
        if to_obj is None:
            raise MappingSetupError('`to_resource` is not defined.')

        # Check if we have already created this mapping
        try:
            return registration.get_mapping(from_obj, to_obj)
        except KeyError:
            pass  # Not registered

        # Get field resolver objects
        try:
            from_fields = registration.get_field_resolver(from_obj)
        except KeyError:
            raise MappingSetupError('`from_resource` %r does not have a attribute resolver defined.' % from_obj)
        try:
            to_fields = registration.get_field_resolver(to_obj)
        except KeyError:
            raise MappingSetupError('`to_resource` %r does not have a attribute resolver defined.' % to_obj)

        def attr_mapping_to_mapping_rule(m, def_type, ref):
            """ Parse, validate and normalise defined mapping rules so rules can be executed without having to perform
            checks during a mapping operation."""
            to_list = False
            bind = False
            skip_if_none = False
            try:
                map_from, action, map_to, to_list, bind, skip_if_none = m
            except ValueError:
                try:
                    map_from, action, map_to = m
                except ValueError:
                    raise MappingSetupError('Bad mapping definition `%s` in %s `%s`.' % (m, def_type, ref))

            map_from = force_tuple(map_from)
            for f in map_from:
                if not f in from_fields:
                    raise MappingSetupError('Field `%s` of %s `%s` not found on from object. ' % (f, def_type, ref))

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
                    raise MappingSetupError('Field `%s` of %s `%s` not found on to object. ' % (f, def_type, ref))

            return map_from, action, map_to, to_list, bind, skip_if_none

        # Determine what fields need to have mappings generated
        exclude_fields = attrs.get('exclude_fields') or tuple()
        unmapped_fields = [attname for attname in from_fields if attname not in exclude_fields]

        def remove_from_unmapped_fields(rule):
            # Remove any fields that are handled by a mapping rule from unmapped_fields list.
            map_from, _, map_to, _, _, _ = rule
            # Removing this in the future as it doesn't really make sense, auto mapped fields are really
            # about mapping to and item not mapping from.
            # if len(map_from) == 1 and map_from[0] in unmapped_fields:
            #     unmapped_fields.remove(map_from[0])
            if len(map_to) == 1 and map_to[0] in unmapped_fields:
                unmapped_fields.remove(map_to[0])

        # Generate mapping rules.
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
                mapping_rules.append(_generate_auto_mapping(field, from_fields, to_fields))

        # Update mappings
        attrs['_mapping_rules'] = mapping_rules

        registration.register_mapping(super_new(cls, name, bases, attrs))
        return registration.get_mapping(from_obj, to_obj)


class MappingBase(object):
    from_resource = None
    to_resource = None

    @classmethod
    def apply(cls, source_resource, context=None):
        """
        Apply conversion either a single resource or a list of resources using the mapping defined by this class.

        If a list of resources is supplied an iterable is returned.

        :param source_resource: The source resource, this must be an instance of :py:attr:`Mapping.from_resource`.
        :param context: An optional context value, this can be any value you want to aid in mapping
        """
        context = context or {}
        context.setdefault('_idx', []).append(0)

        if isinstance(source_resource, (list, tuple)):
            def result_iter(sources, ctx):
                for s in sources:
                    yield cls(s, context).convert()
                    ctx['_idx'][0] += 1
                context['_idx'].pop()
            return result_iter(source_resource, context)
        else:
            try:
                return cls(source_resource, context).convert()
            finally:
                context['_idx'].pop()

    def __init__(self, source_resource, context=None):
        """
        Initialise instance of mapping.

        :param source_resource: The source resource, this must be an instance of :py:attr:`Mapping.from_resource`.
        :param context: An optional context value, this can be any value you want to aid in mapping
        """
        if not isinstance(source_resource, self.from_resource):
            raise TypeError('Source parameter must be an instance of %s' % self.from_resource)
        self.source = source_resource
        self.context = context or {}

    @property
    def loop_idx(self):
        return self.context.setdefault('_idx', [0])[0]

    def _apply_rule(self, mapping_rule):
        # Unpack mapping definition and fetch from values
        from_fields, action, to_fields, to_list, bind, skip_if_none = mapping_rule

        from_values = tuple(getattr(self.source, f) for f in from_fields)

        if action is None:
            to_values = from_values
        else:
            if isinstance(action, six.string_types):
                action = getattr(self, action)

            try:
                if bind:
                    to_values = action(self, *from_values)
                else:
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

        if skip_if_none:
            return {f: to_values[i] for i, f in enumerate(to_fields) if to_values[i] is not None}
        else:
            return {f: to_values[i] for i, f in enumerate(to_fields)}

    def create_object(self, **field_values):
        """Create an instance of target object, this method can be customise to handle custom object initialisation.

        :param field_values: Dictionary of values for creating the target object.
        """
        return self.to_resource(**field_values)

    def convert(self, **field_values):
        """Convert the provided source into a target object.

        :param field_values: Initial field values (or fields not provided by source object);
        """
        assert hasattr(self, '_mapping_rules')

        values = field_values

        for mapping_rule in self._mapping_rules:
            values.update(self._apply_rule(mapping_rule))

        return self.create_object(**values)


class Mapping(six.with_metaclass(MappingMeta, MappingBase)):
    """
    Definition of a mapping between two Objects.
    """
    exclude_fields = []
    mappings = []


def map_field(func=None, from_field=None, to_field=None, to_list=False):
    """
    Field decorator for custom mappings.

    :param from_field: Name of the field to map from; default is to use the function name.
    :param to_field: Name of the field to map to; default is to use the function name.
    :param to_list: Assume the result is a list (rather than a multi value tuple).
    """
    def inner(func):
        func._mapping = define(
            from_field or func.__name__,
            func.__name__,
            to_field or func.__name__,
            to_list
        )
        return func

    return inner(func) if func else inner


def map_list_field(*args, **kwargs):
    """
    Field decorator for custom mappings that return a single list.

    This mapper also allows for returning an iterator or generator that will be converted into a list during the
    mapping operation.

    Parameters are identical to the :py:meth:`map_field` method except ``to_list`` which is forced to be True.
    """
    kwargs['to_list'] = True
    return map_field(*args, **kwargs)
