import copy
from collections.abc import Callable, Sequence
from typing import (
    Any,
    TypeVar,
    cast,
)

from odin import bases, exceptions, registration
from odin.exceptions import ResourceDefError, ValidationError
from odin.fields import BaseField, Field, NotProvided, NotProvidedType
from odin.utils import cached_property, field_iter_items, force_tuple, getmeta

DEFAULT_TYPE_FIELD = "$"

# Set of field names that cannot be used
RESERVED_FIELD_NAMES = {
    "fields",  # Causes an infinite-recursion with clean_fields being a builtin method
}


class ResourceOptions:
    """Shared options used by resource instances."""

    META_OPTION_NAMES = (
        "name",
        "namespace",
        "name_space",
        "verbose_name",
        "verbose_name_plural",
        "abstract",
        "doc_group",
        "type_field",
        "key_field_name",
        "key_field_names",
        "field_name_format",
        "field_sorting",
        "user_data",
        "allow_field_shadowing",
    )

    def __init__(self, meta):
        """Initialise resource options."""
        self.meta = meta
        self.parents = []

        self.fields: list[Field] = []
        self._key_fields: list[Field] = []
        self.virtual_fields: list[BaseField] = []

        self.name: str | None = None
        self.class_name: str | None = None
        self.name_space: str | type[NotProvided] = NotProvided
        self.verbose_name: str | None = None
        self.verbose_name_plural: str | None = None
        self.abstract: bool = False
        self.doc_group: str | None = None
        self.type_field: str | NotProvidedType = NotProvided
        self.key_field_names: Sequence[str] | None = None
        self.field_name_format: Callable[[str], str] | NotProvidedType = NotProvided
        self.field_sorting: bool | NotProvidedType = NotProvided
        self.user_data: Any | None = None
        self.allow_field_shadowing: bool | NotProvidedType = NotProvided

        self._cache = {}

    def __repr__(self):
        return f"<Options for {self.resource_name}>"

    def contribute_to_class(self, cls, _):
        """Contribute option to a resource class."""
        cls._meta = self
        self.name = cls.__name__
        self.class_name = f"{cls.__module__}.{cls.__name__}"

        if self.meta:
            meta_attrs = {
                name: value
                for name, value in self.meta.__dict__.copy().items()
                if not name.startswith("_")
            }

            for attr_name in self.META_OPTION_NAMES:
                if attr_name in meta_attrs:
                    value = meta_attrs.pop(attr_name)

                    # Allow meta to be defined as namespace
                    if attr_name == "namespace":
                        self.name_space = value

                    # Allow key_field_names to be defined as key_field_name
                    elif attr_name == "key_field_name":
                        self.key_field_names = [value]

                    else:
                        setattr(self, attr_name, value)

                elif hasattr(self.meta, attr_name):
                    setattr(self, attr_name, getattr(self.meta, attr_name))

            # Any leftover attributes must be invalid.
            if meta_attrs != {}:
                raise TypeError(
                    f"'class Meta' got invalid attribute(s): {','.join(meta_attrs.keys())}"
                )
        del self.meta

        # Ensure key fields is a tuple
        self.key_field_names = force_tuple(self.key_field_names)

        if not self.verbose_name:
            self.verbose_name = self.name.replace("_", " ").strip("_ ")
        if not self.verbose_name_plural:
            self.verbose_name_plural = self.verbose_name + "s"

    def inherit_from(self, base: "ResourceOptions"):
        """Inherit options from a base meta options instance."""
        if base:
            # Namespace is inherited and default if not provided
            if self.name_space is NotProvided:
                self.name_space = base.name_space

            # Type field is inherited and default if not provided
            if self.type_field is NotProvided:
                self.type_field = base.type_field

            # Key field is inherited
            if self.key_field_names is None:
                self.key_field_names = base.key_field_names

        if self.allow_field_shadowing is NotProvided:
            self.allow_field_shadowing = base.allow_field_shadowing if base else False

        # Field name format is inherited
        if self.field_name_format is NotProvided:
            self.field_name_format = base.field_name_format if base else None

        # Field sorting is inherited
        if self.field_sorting is NotProvided:
            self.field_sorting = base.field_sorting if base else False

    def _add_key_field(self, field):
        self._key_fields.append(field)

    def add_field(self, field):
        """Dynamically add a field."""
        if field.attname in RESERVED_FIELD_NAMES:
            raise ResourceDefError(
                f"`{field.attname}` is a reserved name. Use the `name` argument "
                f"to specify the name used for serialisation."
            )
        self.fields.append(field)
        if field.key:
            self._add_key_field(field)
        cached_property.clear_caches(self)

    def add_virtual_field(self, field):
        """Dynamically add a virtual field."""
        self.virtual_fields.append(field)
        if field.key:
            self._add_key_field(field)
        cached_property.clear_caches(self)

    @property
    def resource_name(self) -> str:
        """Full name of resource including namespace (if specified)."""
        if self.name_space:
            return f"{self.name_space}.{self.name}"
        else:
            return self.name

    @cached_property
    def all_fields(self) -> Sequence[BaseField]:
        """All fields both standard and virtual."""
        return tuple(cast(BaseField, self.fields) + self.virtual_fields)

    @cached_property
    def init_fields(self) -> Sequence[Field]:
        """Fields used in the resource init."""
        return self.fields

    @cached_property
    def shadow_fields(self) -> Sequence[Field]:
        """Fields that are shadowing fields on base classes."""
        return tuple(f for f in self.fields if hasattr(f, "_shadow"))

    @cached_property
    def composite_fields(self) -> Sequence[Field]:
        """All composite fields."""
        # Not the nicest solution but is a fairly safe way of detecting a composite field.
        return tuple(
            f
            for f in self.fields
            if (hasattr(f, "of") and issubclass(f.of, ResourceBase))
        )

    @cached_property
    def container_fields(self) -> Sequence[Field]:
        """All composite fields with the container flag.

        Used by XML like codecs.
        """
        return tuple(
            f for f in self.composite_fields if getattr(f, "use_container", False)
        )

    @cached_property
    def field_map(self) -> dict[str, Field]:
        """Mapping of attribute name to field."""
        return {f.attname: f for f in self.fields}

    @cached_property
    def parent_resource_names(self):
        """List of parent resource names."""
        return tuple(getmeta(p).resource_name for p in self.parents)

    @cached_property
    def attribute_fields(self) -> Sequence[Field]:
        """List of fields where is_attribute is True."""
        return tuple(f for f in self.fields if f.is_attribute)

    @cached_property
    def element_fields(self) -> Sequence[Field]:
        """List of fields where is_attribute is False."""
        return tuple(f for f in self.fields if not f.is_attribute)

    @cached_property
    def element_field_map(self) -> dict[str, Field]:
        """Mapping of attribute name to field for element fields."""
        return {f.attname: f for f in self.element_fields}

    @cached_property
    def key_field(self) -> Field:
        """Field specified as the key field."""
        if self.key_fields:
            return self.key_fields[0]

    @cached_property
    def key_fields(self) -> Sequence[Field]:
        """Tuple of fields specified as the key fields"""
        # Key fields names in meta go first
        field_names = set(self.key_field_names) if self.key_field_names else set()

        # Move over any fields defined as keys
        if self._key_fields:
            field_names.update(f.attname for f in self._key_fields)

        return tuple(sorted((self.field_map[f] for f in field_names), key=hash))

    @cached_property
    def readonly_fields(self) -> Sequence[BaseField]:
        """Fields that can only be read from."""
        return self.virtual_fields

    def check(self):
        """Run checks on meta data to ensure correctness"""


MOT = TypeVar("MOT", bound=ResourceOptions)


def _new_meta_instance(
    meta_options_type: type[MOT],
    meta_def: object | None,
    new_class: "ResourceType",
) -> MOT:
    """Instantiate meta options instance and handle inheritance of required fields."""
    base_meta = getattr(new_class, "_meta", None)
    new_meta = meta_options_type(meta_def)
    new_class.add_to_class("_meta", new_meta)
    new_meta.inherit_from(base_meta)

    # Namespace is inherited
    if new_meta.name_space is NotProvided:
        new_meta.name_space = new_class.__module__

    # Type field is inherited and default if not provided
    if new_meta.type_field is NotProvided:
        new_meta.type_field = DEFAULT_TYPE_FIELD

    return new_meta


def _add_parent_fields_to_class(
    new_class: "ResourceType", new_meta: ResourceOptions, parents
):
    """Iterate through parent attrs and yield fields."""
    # All the fields of any type declared on this model
    field_attr_names = {f.attname for f in new_meta.fields}
    added_attr_names = set()

    for base, base_meta in (
        (base, getmeta(base)) for base in parents if hasattr(base, "_meta")
    ):
        # Check for locally declared fields that are shadowing fields on the base class
        shadow_fields = field_attr_names.intersection(
            f.attname for f in base_meta.all_fields
        )
        if shadow_fields:
            if new_meta.allow_field_shadowing:
                for field in (
                    f for f in base_meta.fields if f.attname in shadow_fields
                ):
                    field._shadow = field
            else:
                msg = (
                    f"Local field{'s' if len(shadow_fields) > 1 else ''} "
                    f"{', '.join(repr(f) for f in shadow_fields)} in class {new_meta.name!r} "
                    f"clashes with field from base class {base.__name__!r}"
                )
                raise Exception(msg)

        # Clone fields (but filter out fields already inherited)
        for field in (
            field for field in base_meta.fields if field.attname not in added_attr_names
        ):
            added_attr_names.add(field.attname)
            new_class.add_to_class(field.attname, copy.deepcopy(field))

        # Clone any virtual fields
        for field in base_meta.virtual_fields:
            new_class.add_to_class(field.attname, copy.deepcopy(field))

        # Add to parents list
        new_meta.parents += base_meta.parents
        new_meta.parents.append(base)


class ResourceType(type):
    """Metaclass for all Resources."""

    meta_options = ResourceOptions

    def __new__(mcs, name, bases, attrs):
        super_new = super().__new__

        # attrs will never be empty for classes declared in the standard way
        # (i.e. with the `class` keyword). This is quite robust.
        if name == "NewBase" and attrs == {}:
            return super_new(mcs, name, bases, attrs)

        parents = [
            b
            for b in bases
            if isinstance(b, ResourceType)
            and not (b.__name__ == "NewBase" and b.__mro__ == (b, object))
        ]
        if not parents:
            # If this isn't a subclass of Resource, don't do anything special.
            return super_new(mcs, name, bases, attrs)

        # Create the class.
        new_class = super_new(mcs, name, bases, {"__module__": attrs.pop("__module__")})

        # Create new meta instance
        new_meta = _new_meta_instance(
            mcs.meta_options, attrs.pop("Meta", None), new_class
        )

        # Bail out early if we have already created this class.
        r = registration.get_resource(new_meta.resource_name)
        if r is not None:
            return r

        # Add all attributes to the class.
        for obj_name, obj in attrs.items():
            new_class.add_to_class(obj_name, obj)

        _add_parent_fields_to_class(new_class, new_meta, parents)

        # Sort the fields
        if new_meta.field_sorting:
            if callable(new_meta.field_sorting):
                new_meta.fields = new_meta.field_sorting(new_meta.fields)
            else:
                new_meta.fields = sorted(new_meta.fields, key=hash)

        # If a key_field is defined ensure it exists
        for field_name in new_meta.key_field_names or ():
            if field_name not in new_meta.field_map:
                raise AttributeError(
                    f"Key field `{field_name}` does not exist on this resource."
                )

        # Give fields an opportunity to do additional operations after the
        # resource is full populated and ready.
        for field in new_meta.all_fields:
            if hasattr(field, "on_resource_ready"):
                field.on_resource_ready()

        if new_meta.abstract:
            return new_class

        # Register resource
        registration.register_resources(new_class)

        # Because of the way imports happen (recursively), we may or may not be
        # the first time this model tries to register with the framework. There
        # should only be one class for each model, so we always return the
        # registered version.
        return registration.get_resource(new_meta.resource_name)

    def add_to_class(cls, name, value):
        if hasattr(value, "contribute_to_class"):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)


class ResourceBase:
    def __init__(self, *args, **kwargs):
        args_len = len(args)
        meta = getmeta(self)
        if args_len > len(meta.init_fields):
            raise TypeError(
                f"This resource takes {len(meta.init_fields)} positional "
                f"arguments but {args_len} where given."
            )

        # The ordering of the zip calls matter - zip throws StopIteration
        # when an iter throws it. So if the first iter throws it, the second
        # is *not* consumed. We rely on this, so don't change the order
        # without changing the logic.
        fields_iter = iter(meta.init_fields)
        if args_len:
            if not kwargs:
                for val, field in zip(args, fields_iter, strict=False):
                    setattr(self, field.attname, val)
            else:
                for val, field in zip(args, fields_iter, strict=False):
                    setattr(self, field.attname, val)
                    kwargs.pop(field.name, None)

        # Now we're left with the unprocessed fields that *must* come from
        # keywords, or default.
        for field in fields_iter:
            try:
                val = kwargs.pop(field.attname)
            except KeyError:
                val = field.get_default()
            setattr(self, field.attname, val)

        if kwargs:
            raise TypeError(
                f"'{list(kwargs)[0]}' is an invalid keyword argument for this function"
            )

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self}>"

    def __str__(self):
        return f"{getmeta(self).resource_name} resource"

    @classmethod
    def create_from_dict(cls, d, full_clean=False):
        """Create a resource instance from a dictionary."""
        return create_resource_from_dict(d, cls, full_clean)

    def to_dict(self, include_virtual=True):
        """Convert this resource into a `dict` of field_name/value pairs.

        .. note::
            This method is not recursive, it only operates on this single resource, any sub resources are returned
            as is. The use case that prompted the creation of this method is within codecs when a resource must be
            converted into a type that can be serialised, these codecs then operate recursively on the returned
            `dict`.

        :param include_virtual: Include virtual fields when generating `dict`.
        """
        meta = getmeta(self)
        fields = meta.all_fields if include_virtual else meta.fields
        return {f.name: v for f, v in field_iter_items(self, fields)}

    def convert_to(self, to_resource, context=None, ignore_fields=None, **field_values):
        """Convert this resource into a specified resource.

        A mapping must be defined for conversion between this resource and to_resource or an exception will be
        raised.
        """
        mapping = registration.get_mapping(self.__class__, to_resource)
        ignore_fields = ignore_fields or []
        ignore_fields.extend(mapping.exclude_fields)
        self.full_clean(ignore_fields)
        return mapping(self, context).convert(**field_values)

    def update_existing(
        self,
        dest_obj,
        context=None,
        ignore_fields=None,
        fields=None,
        ignore_not_provided=False,
    ):
        """Update the fields on an existing destination object.

        A mapping must be defined for conversion between this resource and ``dest_obj`` type or an exception will be
        raised.
        """
        self.full_clean(ignore_fields, ignore_not_provided)
        mapping = registration.get_mapping(self.__class__, dest_obj.__class__)
        return mapping(self, context).update(
            dest_obj, ignore_fields, fields, ignore_not_provided
        )

    def extra_attrs(self, attrs):
        """Called during de-serialisation of data if there are any extra fields defined in the document.

        This allows the resource to decide how to handle these fields. By default they are ignored.
        """

    def clean(self):
        """Chance to do more in depth validation."""

    def full_clean(self, exclude=None, ignore_not_provided=False):
        """Calls clean_fields, clean on the resource and raises ``ValidationError``
        for any errors that occurred.
        """
        errors = {}

        try:
            self.clean_fields(exclude, ignore_not_provided)
        except ValidationError as e:
            errors = e.update_error_dict(errors)

        try:
            self.clean()
        except ValidationError as e:
            errors = e.update_error_dict(errors)

        if errors:
            raise ValidationError(errors)

    def clean_fields(self, exclude=None, ignore_not_provided=False):
        errors = {}
        meta = getmeta(self)

        for f in meta.fields:
            if exclude and f.name in exclude:
                continue

            raw_value = f.value_from_object(self)

            if (f.null and raw_value is None) or (
                ignore_not_provided and raw_value is NotProvided
            ):
                continue

            try:
                raw_value = f.clean(raw_value)
            except ValidationError as e:
                errors[f.name] = e.messages

            # Check for resource level clean methods.
            clean_method = getattr(self, f"clean_{f.attname}", None)
            if callable(clean_method):
                try:
                    raw_value = clean_method(raw_value)
                except ValidationError as e:
                    errors.setdefault(f.name, []).extend(e.messages)

            if f not in meta.readonly_fields:
                setattr(self, f.attname, raw_value)

        if errors:
            raise ValidationError(errors)


class Resource(ResourceBase, metaclass=ResourceType):
    """Resource object"""


def resolve_resource_type(
    resource: type[ResourceBase],
) -> tuple[str | type[ResourceBase], str, str]:
    if isinstance(resource, type) and issubclass(resource, ResourceBase):
        meta = getmeta(resource)
        return meta.resource_name, meta.type_field, meta.name_space
    else:
        return resource, DEFAULT_TYPE_FIELD, ""


def create_resource_from_iter(
    i, resource, full_clean=True, default_to_not_provided=False
):
    """Create a resource from an iterable sequence

    :param i: Iterable of values (it is assumed the values are in field order)
    :param resource: A resource type, resource name or list of resources and names to use as the base for creating a
        resource.
    :param full_clean: Perform a full clean as part of the creation, this is useful for parsing data with known
        columns (eg CSV data).
    :param default_to_not_provided: If an value is not supplied keep the value as NotProvided. This is used
        to support merging an updated value.
    :return: New instance of resource type specified in the *resource* param.
    """
    i = list(i)
    resource_type = resource
    fields = getmeta(resource_type).fields

    # Optimisation to allow the assumption that len(fields) == len(i)
    len_fields = len(fields)
    len_i = len(i)
    extra = None
    if len_i < len_fields:
        i += [NotProvided] * (len_fields - len_i)
    elif len_i > len_fields:
        extra = i[len_fields:]
        i = i[:len_fields]

    attrs = []
    errors = {}
    for f, raw_value in zip(fields, i, strict=False):
        value = raw_value
        if raw_value is NotProvided:
            if not default_to_not_provided:
                value = f.get_default() if f.use_default_if_not_provided else None
        else:
            try:
                value = f.to_python(raw_value)
            except ValidationError as ve:
                errors[f.name] = ve.error_messages
        attrs.append(value)

    if errors:
        raise ValidationError(errors)

    new_resource = resource_type(*attrs)
    if extra:
        new_resource.extra_attrs(extra)
    if full_clean:
        new_resource.full_clean()
    return new_resource


R = TypeVar("R")


def _resolve_type_from_resource(data, resource):
    """Resolve resource type from resource(s)

    If a data type is supplied check it is correct.
    """
    resource_type = None

    # Convert to single resource then resolve document type
    if isinstance(resource, tuple | list):
        resources = (resolve_resource_type(r) for r in resource)
    else:
        resources = [resolve_resource_type(resource)]

    for resource_name, type_field, name_space in resources:
        # See if the input includes a type field and check it's registered
        document_resource_name = data.get(type_field, None)
        if document_resource_name:
            resource_type = registration.get_resource(document_resource_name)
            # Fall back to try applying a prefix
            if not resource_type and name_space:
                resource_type = registration.get_resource(
                    f"{name_space}.{document_resource_name}"
                )
        else:
            resource_type = registration.get_resource(resource_name)

        if not resource_type:
            raise exceptions.ResourceException(
                f"Resource {document_resource_name or resource_name!r} is not registered."
            )

        if document_resource_name:
            # Check resource types match or are inherited types
            if (
                resource_name == document_resource_name
                or resource_name in getmeta(resource_type).parent_resource_names
            ):
                break  # We are done
        else:
            break

    if not resource_type:
        raise exceptions.ResourceException(
            f"Incoming resource does not match [{', '.join(r for r, t in resources)}]"
        )

    return resource_type


def _resolve_type_from_data(data):
    """Resolve type entirely from data"""
    # No resource specified, rely on type field
    document_resource_name = data.pop(DEFAULT_TYPE_FIELD, None)
    if not document_resource_name:
        raise exceptions.ResourceException("Resource not defined.")

    # Get an instance of a resource type
    resource_type = registration.get_resource(document_resource_name)
    if not resource_type:
        raise exceptions.ResourceException(
            f"Resource {document_resource_name!r} is not registered."
        )

    return resource_type


def create_resource_from_dict(
    d: dict[str, Any],
    resource: type[R] = None,
    full_clean: bool = True,
    copy_dict: bool = True,
    default_to_not_provided: bool = False,
):
    """Create a resource from a dict.

    :param d: dictionary of data.
    :param resource: A resource type, resource name or list of resources and names to use as the base for creating a
        resource. If a list is supplied the first item will be used if a resource type is not supplied; this could
        also be a parent(s) of any resource defined by the dict.
    :param full_clean: Perform a full clean as part of the creation.
    :param copy_dict: Use a copy of the input dictionary rather than destructively processing the input dict.
    :param default_to_not_provided: If a value is not supplied keep the value as NOT_PROVIDED. This is used
        to support merging an updated value.
    """
    if not isinstance(d, dict):
        raise TypeError("`d` must be a dict instance.")

    if copy_dict:
        d = d.copy()

    resource_type = (
        _resolve_type_from_resource(d, resource)
        if resource
        else _resolve_type_from_data(d)
    )

    attrs = []
    errors = {}
    meta = getmeta(resource_type)
    # Extract field attributes
    for f in meta.init_fields:
        value = d.pop(f.name, NotProvided)
        if value is NotProvided:
            if not default_to_not_provided:
                value = f.get_default() if f.use_default_if_not_provided else None
        else:
            try:
                value = f.to_python(value)
            except ValidationError as ve:
                errors[f.name] = ve.error_messages
        attrs.append(value)

    # Stop if there are any errors
    if errors and full_clean:
        raise ValidationError(errors)

    # Create the new instance
    new_resource = resource_type(*attrs)

    if d:
        # If there are any extra attributes let the resource handle them
        new_resource.extra_attrs(d)

    if full_clean:
        # Validate the resource in full
        new_resource.full_clean()

    return new_resource


def build_object_graph(
    d: dict[str, Any],
    resource: type[R] | None = None,
    full_clean: bool = True,
    copy_dict: bool = True,
    default_to_not_supplied: bool = False,
) -> R:
    """Generate an object graph from a dict

    :param d: Dictionary to build from
    :param resource: A resource type, resource name or list of resources and names to use as the base for creating a
        resource. If a list is supplied, the first item will be used if a resource type is not supplied.
    :param full_clean: Perform a full clean once built; default is `True`
    :param copy_dict: Clone the dict before doing build; default is `True`
    :param default_to_not_supplied: If a value is not supplied, keep the value as NOT_PROVIDED. This is used
        to support merging an updated value.
    :raises ValidationError: When building the object graph, any issues discovered are raised as a ValidationError.
    """
    if isinstance(d, dict):
        return create_resource_from_dict(
            d, resource, full_clean, copy_dict, default_to_not_supplied
        )

    if isinstance(d, list):
        return [
            build_object_graph(
                o, resource, full_clean, copy_dict, default_to_not_supplied
            )
            for o in d
        ]

    return d


class ResourceIterable(bases.ResourceIterable):
    """Iterable that yields resources."""

    def __init__(self, sequence):
        self.sequence = sequence

    def __iter__(self):
        yield from self.sequence
