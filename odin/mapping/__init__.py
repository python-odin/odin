# -*- coding: utf-8 -*-
import collections
import six
from odin import registration
from odin.resources import Resource
from odin.fields.composite import ListOf, DictAs
from odin.exceptions import MappingSetupError, MappingExecutionError
from odin.mapping.helpers import MapListOf, MapDictAs, NoOpMapper
from odin.utils import cached_property

__all__ = ('Mapping', 'map_field', 'map_list_field', 'assign_field', 'define')


force_tuple = lambda x: x if isinstance(x, (list, tuple)) else (x,)
EMPTY_LIST = tuple()


def define(from_field=None, action=None, to_field=None, to_list=False, bind=False, skip_if_none=False):
    """
    Helper method for defining a mapping.

    :param from_field: Source field to map from.
    :param action: Action callable to perform during mapping, accepted fields differ based on options.
    :param to_field: Destination field to map to; if not specified the from_field
    :param to_list: Assume the result is a list (rather than a multi value tuple).
    :param bind: During the mapping operation the first parameter should be the mapping instance.
    :param skip_if_none: If the from field is :const:`None` do not include the field (this allows the destination
        object to define it's own defaults etc)
    :return: A mapping definition.

    """
    if from_field is None and to_field is None:
        raise MappingSetupError("Either `from_field` or `to_field` must be defined.")
    return from_field, action, to_field or from_field, to_list, bind, skip_if_none


class FieldResolverBase(object):
    """Base class for field resolver objects"""
    def __init__(self, obj):
        self.obj = obj

    @cached_property
    def from_field_dict(self):
        """Property accessor for the attribute dict"""
        return self.get_from_field_dict()

    def get_from_field_dict(self):
        """ Return a field map of source fields consisting of an attribute and a Field object (if one is used).

        For resource objects the field object would be an Odin resource field, for Django models a model field etc. If
        you are building a generic object mapper the field object can be :const:`None`.

        The field object is used to determine certain automatic mapping operations (ie Lists of Odin resources to other
        Odin resources).

        :return: Dictionary
        """
        return self.get_field_dict()

    @cached_property
    def to_field_dict(self):
        """Property accessor for the attribute dict"""
        return self.get_to_field_dict()

    def get_to_field_dict(self):
        """ Return a field map consisting of an attribute and a Field object (if one is used).

        For resource objects the field object would be an Odin resource field, for Django models a model field etc. If
        you are building a generic object mapper the field object can be :const:`None`.

        The field object is used to determine certain automatic mapping operations (ie Lists of Odin resources to other
        Odin resources).

        :return: Dictionary
        """
        return self.get_field_dict()

    def get_field_dict(self):
        """ Return a field map consisting of an attribute and a Field object (if one is used).

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
    name = force_tuple(name)

    # Handle ListOf fields
    if isinstance(from_field, ListOf) and isinstance(to_field, ListOf):
        try:
            mapping = registration.get_mapping(from_field.of, to_field.of)
            return define(name, MapListOf(mapping), name, to_list=True, bind=True)
        except KeyError:
            # If both items are from and to fields refer to the same object automatically use a mapper that just
            # produces a clone.
            if from_field.of is to_field.of:
                return define(name, MapListOf(NoOpMapper), name, to_list=False, bind=True)

    # Handle DictAs fields
    elif isinstance(from_field, DictAs) and isinstance(to_field, DictAs):
        try:
            mapping = registration.get_mapping(from_field.of, to_field.of)
            return define(name, MapDictAs(mapping), name, bind=True)
        except KeyError:
            # If both items are from and to fields refer to the same object automatically use a mapper that just
            # produces a clone.
            if from_field.of is to_field.of:
                return define(name, MapDictAs(NoOpMapper), name, bind=True)

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

        # Backward compatibility from_resource -> from_obj
        from_obj = attrs.setdefault('from_obj', attrs.get('from_resource'))
        if from_obj is None:
            raise MappingSetupError('`from_obj` is not defined.')
        to_obj = attrs.setdefault('to_obj', attrs.get('to_resource'))
        if to_obj is None:
            raise MappingSetupError('`to_obj` is not defined.')

        # Check if we have already created this mapping
        try:
            return registration.get_mapping(from_obj, to_obj)
        except KeyError:
            pass  # Not registered

        # Get field resolver objects
        try:
            from_fields = registration.get_field_resolver(from_obj).from_field_dict
        except KeyError:
            raise MappingSetupError('`from_obj` %r does not have an attribute resolver defined.' % from_obj)
        try:
            to_fields = registration.get_field_resolver(to_obj).to_field_dict
        except KeyError:
            raise MappingSetupError('`to_obj` %r does not have an attribute resolver defined.' % to_obj)

        def attr_mapping_to_mapping_rule(m, def_type, ref):
            """ Parse, validate and normalise defined mapping rules so rules can be executed without having to perform
            checks during a mapping operation."""
            to_list = False
            bind = False
            skip_if_none = False
            is_assignment = False
            try:
                map_from, action, map_to, to_list, bind, skip_if_none = m
            except ValueError:
                try:
                    map_from, action, map_to = m
                except ValueError:
                    raise MappingSetupError('Bad mapping definition `%s` in %s `%s`.' % (m, def_type, ref))

            if map_from is None:
                is_assignment = True

            if not is_assignment:
                map_from = force_tuple(map_from)
                for f in map_from:
                    if f not in from_fields:
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
            elif action is None and is_assignment:
                raise MappingSetupError('No action supplied for `%s` in `%s`.' % (def_type, ref))

            map_to = force_tuple(map_to)
            if to_list and len(map_to) != 1:
                raise MappingSetupError('The %s `%s` specifies a to_list mapping, these can only be applied to a '
                                        'single target field.' % (def_type, m))
            for f in map_to:
                if f not in to_fields:
                    raise MappingSetupError('Field `%s` of %s `%s` not found on to object. ' % (f, def_type, ref))

            return map_from, action, map_to, to_list, bind, skip_if_none

        # Determine what fields need to have mappings generated
        exclude_fields = attrs.get('exclude_fields') or tuple()
        unmapped_fields = [attname for attname in from_fields if attname not in exclude_fields]

        def remove_from_unmapped_fields(rule):
            # Remove any fields that are handled by a mapping rule from unmapped_fields list.
            map_to = rule[2]
            if len(map_to) == 1 and map_to[0] in unmapped_fields:
                unmapped_fields.remove(map_to[0])

        # Generate mapping rules.
        mapping_rules = []

        # Check that from_obj is a sub_class (or same class) as any `parent.from_obj`. This is important for mapping
        # sub class lists and resolving mappings.
        base_parents = [p for p in parents if hasattr(p, '_subs')]
        for p in base_parents:
            if not issubclass(from_obj, p.from_obj):
                raise MappingSetupError('`from_obj` must be a subclass of `parent.from_obj`')
            if not issubclass(to_obj, p.to_obj):
                raise MappingSetupError('`to_obj` must be a subclass of `parent.to_obj`')

            # Copy mapping rules
            for mapping_rule in p._mapping_rules:
                mapping_rules.append(mapping_rule)
                remove_from_unmapped_fields(mapping_rule)

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

        # Update attributes
        attrs['_mapping_rules'] = mapping_rules
        attrs['_subs'] = {}

        registration.register_mapping(super_new(cls, name, bases, attrs))
        mapper = registration.get_mapping(from_obj, to_obj)

        # Register mapping with parents mapping objects as a sub class.
        for parent in base_parents:
            parent._subs[from_obj] = mapper

        return mapper


class MappingResult(object):
    """
    Iterator used to return a sequence from a mapping operation (used by ``Mapping.apply``).
    """
    def __init__(self, sequence, mapping, context=None, *mapping_options):
        self.sequence = sequence
        self.mapping = mapping
        self.context = context or {}
        self.context.setdefault('_loop_idx', [])
        self.mapping_options = mapping_options

    def __iter__(self):
        self.context['_loop_idx'].append(0)
        for item in self.sequence:
            yield self.mapping.apply(item, self.context, *self.mapping_options)
            self.context['_loop_idx'][0] += 1
        self.context['_loop_idx'].pop()


class MappingBase(object):
    from_obj = None
    to_obj = None

    # Pending deprecation, move to from_obj and to_obj terminology
    from_resource = None
    to_resource = None

    @classmethod
    def apply(cls, source_obj, context=None, allow_subclass=False):
        """
        Apply conversion either a single resource or a list of resources using the mapping defined by this class.

        If a list of resources is supplied an iterable is returned.

        :param source_obj: The source resource, this must be an instance of :py:attr:`Mapping.from_obj`.
        :param context: An optional context value, this can be any value you want to aid in mapping
        """
        context = context or {}
        context.setdefault('_loop_idx', [])

        if isinstance(source_obj, (list, tuple)) or hasattr(source_obj, '__iter__'):
            return MappingResult(source_obj, cls, context, allow_subclass)
        elif source_obj.__class__ is cls.from_obj:
            return cls(source_obj, context).convert()
        else:
            # Sub class lookup required
            sub_mapping = cls._subs.get(source_obj.__class__)
            if sub_mapping:
                return sub_mapping(source_obj, context).convert()
            if allow_subclass:
                if allow_subclass and isinstance(source_obj, cls.from_obj):
                    return cls(source_obj, context, True).convert()

                raise TypeError('`source_resource` parameter must be an instance (or subclass instance) of %s' %
                                cls.from_obj)

            raise TypeError('`source_resource` parameter must be an instance of %s' % cls.from_obj)

    def __init__(self, source_obj, context=None, allow_subclass=False):
        """
        Initialise instance of mapping.

        :param source_obj: The source resource, this must be an instance of :py:attr:`Mapping.from_obj`.
        :param context: An optional context value, this can be any value you want to aid in mapping
        """
        if allow_subclass:
            if not isinstance(source_obj, self.from_obj):
                raise TypeError('`source_resource` parameter must be an instance of subclass of %s' % self.from_obj)
        else:
            if source_obj.__class__ is not self.from_obj:
                raise TypeError('`source_resource` parameter must be an instance of %s' % self.from_obj)
        self.source = source_obj
        self.context = context or {}

    @property
    def loop_idx(self):
        """
        Index within a loop of this mapping (note loop might be for a parent object)
        :returns: Index within the loop; or `None` if we are not currently in a loop.
        """
        loops = self.context.setdefault('_loop_idx', [])
        return loops[0] if loops else None

    @property
    def loop_level(self):
        """
        How many layers of loops are we in?
        """
        return len(self.context.setdefault('_loop_idx', []))

    @property
    def in_loop(self):
        """
        Is this mapping currently in a loop?
        """
        return bool(self.context.setdefault('_loop_idx', []))

    def _apply_rule(self, mapping_rule):
        # Unpack mapping definition and fetch from values
        from_fields, action, to_fields, to_list, bind, skip_if_none = mapping_rule

        # This is an assignment rather than a mapping
        if from_fields is None:
            from_values = EMPTY_LIST
        else:
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
            raise MappingExecutionError('Rule expects %s fields (%s returned) applying rule %s' % (
                len(to_fields), len(to_values), mapping_rule))

        if skip_if_none:
            return {f: to_values[i] for i, f in enumerate(to_fields) if to_values[i] is not None}
        else:
            return {f: to_values[i] for i, f in enumerate(to_fields)}

    def create_object(self, **field_values):
        """
        Create an instance of target object, this method can be customise to handle custom object initialisation.

        :param field_values: Dictionary of values for creating the target object.

        """
        return self.to_obj(**field_values)

    def convert(self, **field_values):
        """
        Convert the provided source into a destination object.

        :param field_values: Initial field values (or fields not provided by source object);

        """
        assert hasattr(self, '_mapping_rules')

        values = field_values

        for mapping_rule in self._mapping_rules:
            values.update(self._apply_rule(mapping_rule))

        return self.create_object(**values)

    def update(self, destination_obj, ignore_fields=None):
        """
        Update an existing object with fields from the provided source object.

        :param destination_obj: The existing destination object.
        :param ignore_fields: A list of fields that should be ignored eg ID fields

        """
        assert hasattr(self, '_mapping_rules')

        ignore_fields = ignore_fields or []

        for mapping_rule in self._mapping_rules:
            for name, value in self._apply_rule(mapping_rule).items():
                if name not in ignore_fields:
                    setattr(destination_obj, name, value)

        return destination_obj

    def diff(self, destination_obj):
        """
        Return all fields that are different.

        :note: a full mapping operation is performed during the diffing process.

        :param destination_obj: The existing destination object.
        :return: set of fields that vary.

        """
        assert hasattr(self, '_mapping_rules')

        diff_fields = set()
        for mapping_rule in self._mapping_rules:
            for name, value in self._apply_rule(mapping_rule).items():
                if value != getattr(destination_obj, name):
                    diff_fields.add(name)
        return diff_fields


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
    :param to_list: The result is a list (rather than a multi value tuple).
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


def assign_field(func=None, to_field=None, to_list=False):
    """
    Field decorator for assigning a value to destination field without requiring a corresponding source field.

    Allows for the mapping to calculate a value based on the context or other information. Useful when a destination
    objects defaulting mechanism is not able to calculate a default that either applies or is suitable.

    :param to_field: Name of the field to assign value to; default is to use the function name.
    :param to_list: The result is a list (rather than a multi value tuple).
    """
    def inner(func):
        func._mapping = define(
            None,
            func.__name__,
            to_field or func.__name__,
            to_list
        )
        return func

    return inner(func) if func else inner


def mapping_factory(from_obj, to_obj, base_mapping=Mapping, generate_reverse=True,
                    mappings=None, reverse_mappings=None):
    """
    Factory method for generating simple mappings between objects.

    A common use-case for this method is in generating mappings in baldr's ``model_resource_factory`` method that
    auto-generates resources from Django models.

    :param from_obj: Object to map from.
    :param to_obj: Object to map to.
    :param base_mapping: Base mapping class; default is ``odin.Mapping``.
    :param generate_reverse: Generate the reverse of the mapping ie swap from_obj and to_obj.
    :param mappings: User provided mappings (this is equivalent ot ``odin.Mapping.mappings``)
    :param reverse_mappings: User provided reverse mappings (this is equivalent ot ``odin.Mapping.mappings``). Only
        used if ``generate_reverse`` is True.
    :return: if generate_reverse is True a tuple(forward_mapping, reverse_mapping); else just the forward_mapping.

    """
    forward_mapping = type(
        "%sTo%s" % (from_obj.__class__.__name__, to_obj.__class__.__name__),
        (base_mapping, ),
        dict(
            from_obj=from_obj,
            to_obj=to_obj,
            mappings=mappings or dict()
        )
    )

    if generate_reverse:
        reverse_mapping = type(
            "%sTo%s" % (to_obj.__class__.__name__, from_obj.__class__.__name__),
            (base_mapping, ),
            dict(
                from_obj=to_obj,
                to_obj=from_obj,
                mappings=reverse_mappings or dict()
            )
        )

        return forward_mapping, reverse_mapping

    return forward_mapping
