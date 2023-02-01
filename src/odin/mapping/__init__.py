"""Mapping data between resources or other object types."""
import abc
from typing import (
    TypeVar,
    Union,
    Sequence,
    Optional,
    Callable,
    Any,
    NamedTuple,
    Iterable,
    Type,
    Dict,
)

from odin import bases as base_types
from odin import registration
from odin.fields import NotProvided, Field
from odin.resources import ResourceBase
from odin.fields.composite import ListOf, DictAs
from odin.exceptions import MappingSetupError, MappingExecutionError
from odin.mapping.helpers import MapListOf, MapDictAs, NoOpMapper
from odin.utils import cached_property, getmeta

__all__ = ("Mapping", "map_field", "map_list_field", "assign_field", "define", "assign")

_V = TypeVar("_V")
Action = Callable[[Any, "..."], Optional[Any]]
BoundAction = Callable[["Mapping", Any, "..."], Optional[Any]]


def force_tuple(value: Union[_V, Sequence[_V]]) -> Sequence[_V]:
    """Forces a value to be a tuple."""
    if isinstance(value, tuple):
        return value
    if isinstance(value, list):
        return tuple(value)
    return (value,)


EMPTY_LIST = ()


class FieldMapping(NamedTuple):
    """Field mapping definition"""

    from_field: Union[None, str, Sequence[str]]
    action: Union[None, Action, BoundAction]
    to_field: Union[None, str, Sequence[str]]
    to_list: bool
    bind: bool
    skip_if_none: bool


def define(
    from_field: Union[None, str, Sequence[str]] = None,
    action: Union[None, Action, BoundAction] = None,
    to_field: Union[None, str, Sequence[str]] = None,
    to_list: bool = False,
    bind: bool = False,
    skip_if_none: bool = False,
):
    """Helper method for defining a mapping.

    :param from_field: Source field or fields to map from.
    :param action: Callable Action to perform during mapping, if the bind flag is
        used the first parameter is the current mapping instance.
    :param to_field: Destination field to map to; if not specified defaults to
        the from_field
    :param to_list: Assume the result is a list (rather than a multi value tuple).
    :param bind: During the mapping operation the first parameter should be the mapping instance.
    :param skip_if_none: If the from field is :const:`None` do not include the field (this allows the destination
        object to define it's own defaults)
    :return: A mapping definition.

    """
    if from_field is None and to_field is None:
        raise MappingSetupError("Either `from_field` or `to_field` must be defined.")
    return FieldMapping(
        from_field, action, to_field or from_field, to_list, bind, skip_if_none
    )


def assign(
    to_field: Union[str, Sequence[str]],
    action: Union[Action, BoundAction],
    to_list=False,
    bind=True,
    skip_if_none=False,
):
    """
    Helper method for defining an assignment mapping.

    :param to_field: Destination field to map to; if not specified the from_field
    :param action: Action callable to perform during mapping, accepted fields differ based on options.
    :param to_list: Assume the result is a list (rather than a multi value tuple).
    :param bind: During the mapping operation the first parameter should be the mapping instance; defaults to True
    :param skip_if_none: If the from field is :const:`None` do not include the field (this allows the destination
        object to define it's own defaults etc)
    :return: A mapping definition.

    """
    if to_field is None:
        raise MappingSetupError("`to_field` must be defined.")
    return FieldMapping(None, action, to_field, to_list, bind, skip_if_none)


class FieldResolverBase(abc.ABC):
    """Base class for field resolver objects"""

    def __init__(self, obj):
        self.obj = obj

    @cached_property
    def from_field_dict(self) -> Dict[str, Optional[Field]]:
        """Property accessor for the attribute dict"""
        return self.get_from_field_dict()

    def get_from_field_dict(self) -> Dict[str, Optional[Field]]:
        """Return a field map of source fields consisting of an attribute and a Field object (if one is used).

        For resource objects the field object would be an Odin resource field, for Django models a model field etc. If
        you are building a generic object mapper the field object can be :const:`None`.

        The field object is used to determine certain automatic mapping operations (ie Lists of Odin resources to other
        Odin resources).

        :return: Dictionary

        """
        return self.get_field_dict()

    @cached_property
    def to_field_dict(self) -> Dict[str, Optional[Field]]:
        """Property accessor for the attribute dict"""
        return self.get_to_field_dict()

    def get_to_field_dict(self) -> Dict[str, Optional[Field]]:
        """Return a field map consisting of an attribute and a Field object (if one is used).

        For resource objects the field object would be an Odin resource field, for Django models a model field etc. If
        you are building a generic object mapper the field object can be :const:`None`.

        The field object is used to determine certain automatic mapping operations (ie Lists of Odin resources to other
        Odin resources).

        :return: Dictionary
        """
        return self.get_field_dict()

    @abc.abstractmethod
    def get_field_dict(self) -> Dict[str, Optional[Field]]:
        """Return a field map consisting of an attribute and a Field object (if one is used).

        For resource objects the field object would be an Odin resource field, for Django models a model field etc. If
        you are building a generic object mapper the field object can be :const:`None`.

        The field object is used to determine certain automatic mapping operations (ie Lists of Odin resources to other
        Odin resources).

        :return: Dictionary
        """


class ResourceFieldResolver(FieldResolverBase):
    """Field resolver for Odin resource objects."""

    def get_field_dict(self):
        """Return a dictionary of fields along with their names."""
        return getmeta(self.obj).field_map


registration.register_field_resolver(ResourceFieldResolver, ResourceBase)


class MappingMeta(type):
    """Metaclass for all Mappings"""

    def __new__(mcs, name, bases, attrs):
        super_new = super().__new__

        # attrs will never be empty for classes declared in the standard way
        # (ie. with the `class` keyword). This is quite robust.
        if name == "NewBase" and attrs == {}:
            return super_new(mcs, name, bases, attrs)

        parents = [
            b
            for b in bases
            if isinstance(b, MappingMeta)
            and not (b.__name__ == "NewBase" and b.__mro__ == (b, MappingBase, object))
        ]
        if not parents:
            # If this isn't a subclass of Mapping, don't do anything special.
            return super_new(mcs, name, bases, attrs)

        # Backward compatibility from_resource -> from_obj
        from_obj = attrs.setdefault("from_obj", attrs.get("from_resource"))
        if from_obj is None:
            raise MappingSetupError("`from_obj` is not defined.")
        to_obj = attrs.setdefault("to_obj", attrs.get("to_resource"))
        if to_obj is None:
            raise MappingSetupError("`to_obj` is not defined.")
        register_mapping = attrs.pop("register_mapping", True)

        # Check if we have already created this mapping
        if register_mapping:
            try:
                return registration.get_mapping(from_obj, to_obj)
            except KeyError:
                pass  # Not registered

        # Get field resolver objects
        try:
            from_fields = registration.get_field_resolver(from_obj).from_field_dict
        except KeyError:
            raise MappingSetupError(
                f"`from_obj` {from_obj!r} does not have an attribute resolver defined."
            )
        try:
            to_fields = registration.get_field_resolver(to_obj).to_field_dict
        except KeyError:
            raise MappingSetupError(
                f"`to_obj` {to_obj!r} does not have an attribute resolver defined."
            )

        def attr_mapping_to_mapping_rule(m, def_type, ref):
            """Parse, validate and normalise defined mapping rules so rules can be executed without having to perform
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
                    raise MappingSetupError(
                        f"Bad mapping definition `{m}` in {def_type} `{ref}`."
                    )

            if map_from is None:
                is_assignment = True

            if not is_assignment:
                map_from = force_tuple(map_from)
                for f in map_from:
                    if f not in from_fields:
                        raise MappingSetupError(
                            f"Field `{f}` of {def_type} `{ref}` not found on from object. "
                        )

            if isinstance(action, str):
                if action not in attrs:
                    raise MappingSetupError(
                        f"Action named {action} defined in {def_type} `{ref}` was not defined on "
                        f"mapping object."
                    )
                if not callable(attrs[action]):
                    raise MappingSetupError(
                        f"Action named {action} defined in {def_type} `{ref}` is not callable."
                    )
            elif action is not None and not callable(action):
                raise MappingSetupError(
                    f"Action on {def_type} `{ref}` is not callable."
                )
            elif action is None and is_assignment:
                raise MappingSetupError(
                    f"No action supplied for `{def_type}` in `{ref}`."
                )

            map_to = force_tuple(map_to)
            if to_list and len(map_to) != 1:
                raise MappingSetupError(
                    f"The {def_type} `{m}` specifies a to_list mapping, these can only be "
                    f"applied to a single target field."
                )
            for f in map_to:
                if f not in to_fields:
                    raise MappingSetupError(
                        f"Field `{f}` of {def_type} `{ref}` not found on to object. "
                    )

            return FieldMapping(map_from, action, map_to, to_list, bind, skip_if_none)

        # Determine what fields need to have mappings generated
        exclude_fields = attrs.get("exclude_fields") or ()
        unmapped_fields = [
            attname for attname in from_fields if attname not in exclude_fields
        ]

        def remove_from_unmapped_fields(rule):
            # Remove any fields that are handled by a mapping rule from unmapped_fields list.
            map_to = rule[2]
            if len(map_to) == 1 and map_to[0] in unmapped_fields:
                unmapped_fields.remove(map_to[0])

        # Generate mapping rules.
        mapping_rules = []

        # Check that from_obj is a sub_class (or same class) as any `parent.from_obj`. This is important for mapping
        # sub class lists and resolving mappings.
        base_parents = [p for p in parents if hasattr(p, "_subs")]
        for p in base_parents:
            if not issubclass(from_obj, p.from_obj):
                raise MappingSetupError(
                    "`from_obj` must be a subclass of `parent.from_obj`"
                )
            if not issubclass(to_obj, p.to_obj):
                raise MappingSetupError(
                    "`to_obj` must be a subclass of `parent.to_obj`"
                )

            # Copy mapping rules
            for mapping_rule in p._mapping_rules:
                mapping_rules.append(mapping_rule)
                remove_from_unmapped_fields(mapping_rule)

        # Add basic mappings
        for idx, mapping in enumerate(attrs.pop("mappings", [])):
            mapping_rule = attr_mapping_to_mapping_rule(mapping, "basic mapping", idx)
            mapping_rules.append(mapping_rule)
            remove_from_unmapped_fields(mapping_rule)

        # Add custom mappings
        for attr in attrs.values():
            # Methods with a _mapping attribute have been decorated by either `map_field` or `map_list_field`
            # decorators.
            if hasattr(attr, "_mapping"):
                mapping_rule = attr_mapping_to_mapping_rule(
                    getattr(attr, "_mapping"), "custom mapping", attr
                )
                mapping_rules.append(mapping_rule)
                remove_from_unmapped_fields(mapping_rule)
                # Remove mapping
                delattr(attr, "_mapping")

        # Add auto mapped fields that are yet to be mapped.
        for field in unmapped_fields:
            if field in to_fields:
                mapping_rules.append(
                    mcs.generate_auto_mapping(field, from_fields, to_fields)
                )

        # Update attributes
        attrs["_mapping_rules"] = mapping_rules
        attrs["_subs"] = {}

        # Create mapper instance
        mapper = super_new(mcs, name, bases, attrs)
        if register_mapping:
            registration.register_mapping(mapper)
            mapper = registration.get_mapping(from_obj, to_obj)

            # Register mapping with parents mapping objects as a sub class.
            for parent in base_parents:
                parent._subs[from_obj] = mapper

        return mapper

    @classmethod
    def generate_auto_mapping(mcs, name, from_fields, to_fields):
        """Generate the auto mapping between two fields."""
        from_field = from_fields[name]
        to_field = to_fields[name]
        name = force_tuple(name)

        # Handle ListOf fields
        if isinstance(from_field, ListOf) and isinstance(to_field, ListOf):
            return mcs.generate_list_to_list_mapping(name, from_field, to_field)

        # Handle DictAs fields
        elif isinstance(from_field, DictAs) and isinstance(to_field, DictAs):
            return mcs.generate_dict_to_dict_mapping(name, from_field, to_field)

        return define(name, "default_action")

    @classmethod
    def generate_list_to_list_mapping(mcs, name, from_field, to_field):
        """Generate a mapping of list to list objects."""
        try:
            mapping = registration.get_mapping(from_field.of, to_field.of)
            return FieldMapping(
                name,
                MapListOf(mapping),
                name,
                to_list=False,
                bind=True,
                skip_if_none=False,
            )
        except KeyError:
            # If both items are from and to fields refer to the same object automatically use a mapper that just
            # produces a clone.
            if from_field.of is to_field.of:
                return FieldMapping(
                    name,
                    MapListOf(NoOpMapper),
                    name,
                    to_list=False,
                    bind=True,
                    skip_if_none=False,
                )

    @classmethod
    def generate_dict_to_dict_mapping(mcs, name, from_field, to_field):
        try:
            mapping = registration.get_mapping(from_field.of, to_field.of)
            return define(name, MapDictAs(mapping), name, bind=True)
        except KeyError:
            # If both items are from and to fields refer to the same object automatically use a mapper that just
            # produces a clone.
            if from_field.of is to_field.of:
                return define(name, MapDictAs(NoOpMapper), name, bind=True)


class MappingResult(base_types.TypedResourceIterable):
    """Iterator used lazily return a sequence from a mapping operation (used by ``Mapping.apply``)."""

    def __init__(self, sequence, mapping, context=None, *mapping_options):
        super().__init__(mapping.to_obj)
        self.sequence = sequence
        self.mapping = mapping
        self.context = context or {}
        self.context.setdefault("_loop_idx", [])
        self.mapping_options = mapping_options

    def __iter__(self):
        self.context["_loop_idx"].append(0)
        for item in self.sequence:
            yield self.mapping.apply(item, self.context, *self.mapping_options)
            self.context["_loop_idx"][-1] += 1
        self.context["_loop_idx"].pop()


class ImmediateResult(base_types.ResourceIterable):
    """Immediately performs the mapping operation rather than delay.

    This is useful if context is volatile.
    """

    def __init__(self, *args, **kwargs):
        self.sequence = list(MappingResult(*args, **kwargs))

    def __iter__(self):
        for item in self.sequence:
            yield item


class CachingMappingResult(MappingResult):
    """Extends from the basic MappingResult to cache the results of a mapping operation and also provide methods and
    abilities available to a list (len, indexing). The results are only evaluated when requested.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache: Optional[list] = None

    def __iter__(self):
        if self._cache is None:
            self._cache = []
            for item in super().__iter__():
                self._cache.append(item)
                yield item
        else:
            yield from self._cache

    @property
    def items(self) -> list:
        if self._cache is None:
            list(iter(self))
        return self._cache

    def __len__(self):
        return len(self.items)

    def __getitem__(self, idx):
        return self.items[idx]


class MappingBase:
    from_obj: type = None
    to_obj: type = None

    # Pending deprecation, move to from_obj and to_obj terminology
    from_resource = None
    to_resource = None

    # Default mapping result object to use
    default_mapping_result = CachingMappingResult

    # Register mapping with global registry, if the same resource pair
    # is mapped in different ways then this might want to be set to False
    register_mapping = True

    _mapping_rules = None

    @classmethod
    def apply(
        cls,
        source_obj,
        context=None,
        allow_subclass: bool = False,
        mapping_result: MappingResult = None,
    ):
        """
        Apply conversion either a single resource or a list of resources using the mapping defined by this class.

        If a list of resources is supplied an iterable is returned.

        :param source_obj: The source resource, this must be an instance of :py:attr:`Mapping.from_obj`.
        :param context: An optional context value, this can be any value you want to aid in mapping
        :param allow_subclass: Allow sub-classes of mapping resource to be included.
        :param mapping_result: If an iterable is provided as the source object a mapping result is returned of the type
            specified is returned.

        """
        context = context or {}
        mapping_result = mapping_result or cls.default_mapping_result
        context.setdefault("_loop_idx", [])

        if hasattr(source_obj, "__iter__"):
            return mapping_result(source_obj, cls, context, allow_subclass)
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

                raise TypeError(
                    f"`source_resource` parameter must be an instance (or subclass instance) of {cls.from_obj}"
                )

            raise TypeError(
                f"`source_resource` parameter must be an instance of {cls.from_obj}"
            )

    def __init__(
        self,
        source_obj,
        context=None,
        allow_subclass: bool = False,
        ignore_not_provided: bool = False,
    ):
        """Initialise instance of mapping.

        :param source_obj: The source resource, this must be an instance of :py:attr:`Mapping.from_obj`.
        :param context: An optional context value, this can be any value you want to aid in mapping
        :param allow_subclass:
        :param ignore_not_provided: Ignore values that are `NotProvided`.
        """
        if allow_subclass:
            if not isinstance(source_obj, self.from_obj):
                raise TypeError(
                    f"`source_resource` parameter must be an instance of subclass of {self.from_obj}"
                )
        else:
            if source_obj.__class__ is not self.from_obj:
                raise TypeError(
                    f"`source_resource` parameter must be an instance of {self.from_obj}"
                )
        self.source = source_obj
        self.context = context or {}
        self.ignore_not_provided = ignore_not_provided

    @property
    def loop_idx(self):
        """Index within a loop of this mapping (note loop might be for a parent object)
        :returns: Index within the loop; or `None` if we are not currently in a loop.
        """
        loops = self.context.setdefault("_loop_idx", [])
        return loops[-1] if loops else None

    @property
    def loop_level(self):
        """How many layers of loops are we in?"""
        return len(self.context.setdefault("_loop_idx", []))

    @property
    def in_loop(self):
        """Is this mapping currently in a loop?"""
        return bool(self.context.setdefault("_loop_idx", []))

    def default_action(self, value):
        """The default action used when mapping. This is a bit of a special case in that it defaults to being bound
        and makes use of :func:`functools.partial` to bind the from and to fields.

        :param value: The value to be mapped.
        :return: Mapped value.

        """

        return value

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
            if isinstance(action, str):
                action = getattr(self, action)

            try:
                if bind:
                    to_values = action(self, *from_values)
                else:
                    to_values = action(*from_values)
            except TypeError as ex:
                raise MappingExecutionError(f"{ex} applying rule {mapping_rule}")

        if to_list:
            if isinstance(to_values, Iterable):
                to_values = (list(to_values),)
        else:
            to_values = force_tuple(to_values)

        if len(to_fields) != len(to_values):
            raise MappingExecutionError(
                f"Rule expects {len(to_fields)} fields ({len(to_values)} returned) "
                f"applying rule {mapping_rule}. The `to_list` option might need to be specified"
            )

        if skip_if_none:
            result = {
                f: to_values[i]
                for i, f in enumerate(to_fields)
                if to_values[i] is not None
            }
        else:
            result = {f: to_values[i] for i, f in enumerate(to_fields)}

        if self.ignore_not_provided:
            return {k: v for k, v in result.items() if v is not NotProvided}
        else:
            return result

    def create_object(self, **field_values):
        """Create an instance of target object, this method can be customised to handle
        custom object initialisation.

        :param field_values: Dictionary of values for creating the target object.
        """
        return self.to_obj(**field_values)

    def convert(self, **field_values):
        """Convert the provided source into a destination object.

        :param field_values: Initial field values (or fields not provided by source object);
        """
        values = field_values

        for mapping_rule in self._mapping_rules:
            values.update(self._apply_rule(mapping_rule))

        return self.create_object(**values)

    def update(
        self,
        destination_obj: Any,
        ignore_fields: Sequence[str] = None,
        fields=None,
        ignore_not_provided: bool = False,
    ):
        """Update an existing object with fields from the provided source object.

        :param destination_obj: The existing destination object.
        :param ignore_fields: A list of fields that should be ignored eg ID fields
        :param fields: Collection of fields that should be mapped.
        :param ignore_not_provided: Ignore field values that are `NotDefined`

        """
        ignore_fields = ignore_fields or []

        for mapping_rule in self._mapping_rules:
            for name, value in self._apply_rule(mapping_rule).items():
                if not (
                    (name in ignore_fields)
                    or (fields and name not in fields)
                    or (ignore_not_provided and value is NotProvided)
                ):
                    setattr(destination_obj, name, value)

        return destination_obj

    def diff(self, destination_obj: Any, ignore_not_provided: bool = False):
        """Return all fields that are different.

        :note: a full mapping operation is performed during the diffing process.

        :param destination_obj: The existing destination object.
        :param ignore_not_provided: Ignore field values that are `NotDefined`
        :return: set of fields that vary.

        """
        diff_fields = set()
        for mapping_rule in self._mapping_rules:
            for name, value in self._apply_rule(mapping_rule).items():
                if not (
                    (value == getattr(destination_obj, name))
                    and (ignore_not_provided and value is NotProvided)
                ):
                    diff_fields.add(name)
        return diff_fields


class Mapping(MappingBase, metaclass=MappingMeta):
    """Definition of a mapping between two Objects."""

    exclude_fields = []
    mappings = []


class DynamicMapping(MappingBase):
    """A mapping that is dynamically generated at run time."""


class ImmediateMapping(MappingBase, metaclass=MappingMeta):
    """Definition of a mapping between two Objects.

    This version of the Mapping, defaults to returning an Immediate rather than
    a cached result object.
    """

    exclude_fields = []
    mappings = []

    default_mapping_result = ImmediateResult


def map_field(
    func=None, from_field: str = None, to_field: str = None, to_list: bool = False
):
    """Field decorator for custom mappings.

    :param func: Method being decorator is wrapping.
    :param from_field: Name of the field to map from; default is to use the function name.
    :param to_field: Name of the field to map to; default is to use the function name.
    :param to_list: The result is a list (rather than a multi value tuple).
    """

    def inner(fun):
        fun._mapping = define(
            from_field or fun.__name__, fun.__name__, to_field or fun.__name__, to_list
        )
        return fun

    return inner(func) if func else inner


def map_list_field(*args, **kwargs):
    """Field decorator for custom mappings that return a single list.

    This mapper also allows for returning an iterator or generator that will be converted into a list during the
    mapping operation.

    Parameters are identical to the :py:meth:`map_field` method except ``to_list`` which is forced to be True.
    """
    kwargs["to_list"] = True
    return map_field(*args, **kwargs)


def assign_field(func=None, to_field: str = None, to_list: bool = False):
    """Field decorator for assigning a value to destination field without requiring a corresponding source field.

    Allows for the mapping to calculate a value based on the context or other information. Useful when a destination
    objects defaulting mechanism is not able to calculate a default that either applies or is suitable.

    :param func: Method being decorator is wrapping.
    :param to_field: Name of the field to assign value to; default is to use the function name.
    :param to_list: The result is a list (rather than a multi value tuple).
    """

    def inner(fun):
        fun._mapping = define(None, fun.__name__, to_field or fun.__name__, to_list)
        return fun

    return inner(func) if func else inner


def mapping_factory(
    from_obj: Any,
    to_obj: Any,
    base_mapping: Type[Mapping] = Mapping,
    generate_reverse: bool = True,
    mappings=None,
    reverse_mappings=None,
    exclude_fields=None,
    reverse_exclude_fields=None,
    register_mappings=True,
):
    """Factory method for generating simple mappings between objects.

    A common use-case for this method is in generating mappings in baldr's ``model_resource_factory`` method that
    auto-generates resources from Django models.

    :param from_obj: Object to map from.
    :param to_obj: Object to map to.
    :param base_mapping: Base mapping class; default is ``odin.Mapping``.
    :param generate_reverse: Generate the reverse of the mapping ie swap from_obj and to_obj.
    :param mappings: User provided mappings (this is equivalent ot ``odin.Mapping.mappings``)
    :param reverse_mappings: User provided reverse mappings (this is equivalent ot ``odin.Mapping.mappings``). Only
        used if ``generate_reverse`` is True.
    :param exclude_fields: Fields to exclude from auto-generated mappings
    :param reverse_exclude_fields: Fields to exclude from auto-generated reverse mappings.
    :param register_mappings: Register mapping in mapping lookup cache.
    :return: if generate_reverse is True a tuple(forward_mapping, reverse_mapping); else just the forward_mapping.
    :rtype: Mapping | (Mapping, Mapping)

    """
    forward_mapping = type(
        f"{from_obj.__class__.__name__}{from_obj.__name__}To{to_obj.__class__.__name__}{to_obj.__name__}",
        (base_mapping,),
        {
            "from_obj": from_obj,
            "to_obj": to_obj,
            "exclude_fields": exclude_fields or [],
            "mappings": mappings or {},
            "register_mapping": register_mappings,
        },
    )

    if generate_reverse:
        reverse_mapping = type(
            f"{to_obj.__class__.__name__}{to_obj.__name__}To{from_obj.__class__.__name__}{from_obj.__name__}",
            (base_mapping,),
            {
                "from_obj": to_obj,
                "to_obj": from_obj,
                "exclude_fields": reverse_exclude_fields or [],
                "mappings": reverse_mappings or {},
                "register_mapping": register_mappings,
            },
        )

        return forward_mapping, reverse_mapping

    return forward_mapping


def forward_mapping_factory(
    from_obj: Any,
    to_obj: Any,
    base_mapping: Type[Mapping] = Mapping,
    mappings=None,
    exclude_fields=None,
):
    """Factory method for generating simple forward mappings between objects.

    :param from_obj: Object to map from.
    :param to_obj: Object to map to.
    :param base_mapping: Base mapping class; default is ``odin.Mapping``.
    :param mappings: User provided mappings (this is equivalent ot ``odin.Mapping.mappings``)
    :param exclude_fields: Fields to exclude from auto-generated mappings
    :return: Forward_mapping object.

    """
    return mapping_factory(
        from_obj, to_obj, base_mapping, False, mappings, None, exclude_fields, None
    )


def dynamic_mapping_factory(
    from_obj: Any,
    to_obj: Any,
    base_mapping: Type[Mapping] = Mapping,
    generate_reverse: bool = False,
    mappings=None,
    reverse_mappings=None,
    exclude_fields=None,
    reverse_exclude_fields=None,
):
    """Factory method for generating a dynamic mapping. That is generated dynamically at run time (eg from
    configuration the results of which are not registered for later use.

    :param from_obj: Object to map from.
    :param to_obj: Object to map to.
    :param base_mapping: Base mapping class; default is ``odin.Mapping``.
    :param generate_reverse: Generate the reverse of the mapping ie swap from_obj and to_obj.
    :param mappings: User provided mappings (this is equivalent ot ``odin.Mapping.mappings``)
    :param reverse_mappings: User provided reverse mappings (this is equivalent ot ``odin.Mapping.mappings``). Only
        used if ``generate_reverse`` is True.
    :param exclude_fields: Fields to exclude from auto-generated mappings
    :param reverse_exclude_fields: Fields to exclude from auto-generated reverse mappings.
    :return: if generate_reverse is True a tuple(forward_mapping, reverse_mapping); else just the forward_mapping.
    :rtype: Mapping | (Mapping, Mapping)

    """
    return mapping_factory(
        from_obj,
        to_obj,
        base_mapping,
        generate_reverse,
        mappings,
        reverse_mappings,
        exclude_fields,
        reverse_exclude_fields,
        False,
    )
