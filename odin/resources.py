# -*- coding: utf-8 -*-
import copy
import six
from odin import bases

from odin import exceptions, registration
from odin.exceptions import ValidationError
from odin.fields import NOT_PROVIDED
from odin.utils import cached_property, field_iter_items, force_tuple, getmeta

DEFAULT_TYPE_FIELD = '$'


class ResourceOptions(object):
    META_OPTION_NAMES = (
        'name', 'namespace', 'name_space', 'verbose_name', 'verbose_name_plural', 'abstract', 'doc_group',
        'type_field', 'key_field_name', 'key_field_names'
    )

    def __init__(self, meta):
        self.meta = meta
        self.parents = []
        self.fields = []
        self._key_fields = []
        self.virtual_fields = []

        self.name = None
        self.class_name = None
        self.name_space = NOT_PROVIDED
        self.verbose_name = None
        self.verbose_name_plural = None
        self.abstract = False
        self.doc_group = None
        self.type_field = DEFAULT_TYPE_FIELD
        self.key_field_names = None

        self._cache = {}

    def contribute_to_class(self, cls, _):
        cls._meta = self
        self.name = cls.__name__
        self.class_name = "%s.%s" % (cls.__module__, cls.__name__)

        if self.meta:
            meta_attrs = self.meta.__dict__.copy()
            for name in self.meta.__dict__:
                if name.startswith('_'):
                    del meta_attrs[name]
            for attr_name in self.META_OPTION_NAMES:
                if attr_name in meta_attrs:
                    # Allow meta to be defined as namespace
                    if attr_name == 'namespace':
                        setattr(self, 'name_space', meta_attrs.pop(attr_name))
                    # Allow key_field_names to be defined as key_field_name
                    elif attr_name == 'key_field_name':
                        setattr(self, 'key_field_names', meta_attrs.pop(attr_name))
                    else:
                        setattr(self, attr_name, meta_attrs.pop(attr_name))
                elif hasattr(self.meta, attr_name):
                    setattr(self, attr_name, getattr(self.meta, attr_name))

            # Any leftover attributes must be invalid.
            if meta_attrs != {}:
                raise TypeError("'class Meta' got invalid attribute(s): %s" % ','.join(meta_attrs.keys()))
        del self.meta

        # Ensure key fields is a tuple
        self.key_field_names = force_tuple(self.key_field_names)

        if not self.verbose_name:
            self.verbose_name = self.name.replace('_', ' ').strip('_ ')
        if not self.verbose_name_plural:
            self.verbose_name_plural = self.verbose_name + 's'

    def _add_key_field(self, field):
        self._key_fields.append(field)

    def add_field(self, field):
        self.fields.append(field)
        if field.key:
            self._add_key_field(field)
        cached_property.clear_caches(self)

    def add_virtual_field(self, field):
        self.virtual_fields.append(field)
        if field.key:
            self._add_key_field(field)
        cached_property.clear_caches(self)

    @property
    def resource_name(self):
        """
        Full name of resource including namespace (if specified)
        """
        if self.name_space:
            return "%s.%s" % (self.name_space, self.name)
        else:
            return self.name

    @cached_property
    def all_fields(self):
        """
        All fields both standard and virtual.
        """
        return self.fields + self.virtual_fields

    @cached_property
    def composite_fields(self):
        """
        All composite fields.
        """
        # Not the nicest solution but is a fairly safe way of detecting a composite field.
        return [f for f in self.fields if (hasattr(f, 'of') and issubclass(f.of, Resource))]

    @cached_property
    def container_fields(self):
        """
        All composite fields with the container flag.

        Used by XML like codecs.

        """
        return [f for f in self.composite_fields if getattr(f, 'use_container', False)]

    @cached_property
    def field_map(self):
        return dict((f.attname, f) for f in self.fields)

    @cached_property
    def parent_resource_names(self):
        """
        List of parent resource names.
        """
        return [getmeta(p).resource_name for p in self.parents]

    @cached_property
    def attribute_fields(self):
        """
        List of fields where is_attribute is True.
        """
        return [f for f in self.fields if f.is_attribute]

    @cached_property
    def element_fields(self):
        """
        List of fields where is_attribute is False.
        """
        return [f for f in self.fields if not f.is_attribute]

    @cached_property
    def element_field_map(self):
        return dict((f.attname, f) for f in self.element_fields)

    @cached_property
    def key_field(self):
        """
        Field specified as the key field
        """
        if self.key_fields:
            return self.key_fields[0]

    @cached_property
    def key_fields(self):
        """
        Tuple of fields specified as the key fields
        """
        fields = []

        # Key fields named in meta go first
        if self.key_field_names:
            for field_name in self.key_field_names:
                fields.append(self.field_map[field_name])

        # Move over any fields defined as keys
        if self._key_fields:
            for field in sorted(self._key_fields, key=hash):
                if field.attname not in self.key_field_names:
                    fields.append(field)

        return fields

    def check(self):
        """
        Run checks on meta data to ensure correctness
        """
        pass

    def __repr__(self):
        return '<Options for %s>' % self.resource_name


class ResourceType(type):
    """
    Metaclass for all Resources.
    """
    meta_options = ResourceOptions

    def __new__(mcs, name, bases, attrs):
        super_new = super(ResourceType, mcs).__new__

        # attrs will never be empty for classes declared in the standard way
        # (ie. with the `class` keyword). This is quite robust.
        if name == 'NewBase' and attrs == {}:
            return super_new(mcs, name, bases, attrs)

        parents = [
            b for b in bases if
            isinstance(b, ResourceType) and not (b.__name__ == 'NewBase' and b.__mro__ == (b, object))
        ]
        if not parents:
            # If this isn't a subclass of Resource, don't do anything special.
            return super_new(mcs, name, bases, attrs)

        # Create the class.
        module = attrs.pop('__module__')
        new_class = super_new(mcs, name, bases, {'__module__': module})
        attr_meta = attrs.pop('Meta', None)
        abstract = getattr(attr_meta, 'abstract', False)
        if not attr_meta:
            meta = getattr(new_class, 'Meta', None)
        else:
            meta = attr_meta
        base_meta = getattr(new_class, '_meta', None)

        new_meta = mcs.meta_options(meta)
        new_class.add_to_class('_meta', new_meta)

        # Generate a namespace if one is not provided
        if new_meta.name_space is NOT_PROVIDED and base_meta:
            # Namespace is inherited
            if (not new_meta.name_space) or (new_meta.name_space is NOT_PROVIDED):
                new_meta.name_space = base_meta.name_space

        if new_meta.name_space is NOT_PROVIDED:
            new_meta.name_space = module

        # Key field is inherited
        if base_meta and (not new_meta.key_field_names) or (new_meta.key_field_names is NOT_PROVIDED):
            new_meta.key_field_names = base_meta.key_field_names

        # Bail out early if we have already created this class.
        r = registration.get_resource(new_meta.resource_name)
        if r is not None:
            return r

        # Add all attributes to the class.
        for obj_name, obj in attrs.items():
            new_class.add_to_class(obj_name, obj)

        # Sort the fields
        new_meta.fields = sorted(new_meta.fields, key=hash)

        # All the fields of any type declared on this model
        local_field_attnames = set([f.attname for f in new_meta.fields])
        field_attnames = set(local_field_attnames)

        for base in parents:
            try:
                base_meta = getattr(base, '_meta')
            except AttributeError:
                # Things without _meta aren't functional models, so they're
                # uninteresting parents.
                continue

            # Check for clashes between locally declared fields and those
            # on the base classes (we cannot handle shadowed fields at the
            # moment).
            for field in base_meta.all_fields:
                if field.attname in local_field_attnames:
                    raise Exception('Local field %r in class %r clashes with field of similar name from '
                                    'base class %r' % (field.attname, name, base.__name__))
            for field in base_meta.fields:
                if field.attname not in field_attnames:
                    field_attnames.add(field.attname)
                    new_class.add_to_class(field.attname, copy.deepcopy(field))
            for field in base_meta.virtual_fields:
                new_class.add_to_class(field.attname, copy.deepcopy(field))

            new_meta.parents += base_meta.parents
            new_meta.parents.append(base)

        # If a key_field is defined ensure it exists
        if new_meta.key_field_names:
            for field_name in new_meta.key_field_names:
                if field_name not in new_meta.field_map:
                    raise AttributeError('Key field `{0}` is not exist on this resource.'.format(field_name))

        # Give fields an opportunity to do additional operations after the
        # resource is full populated and ready.
        for field in new_meta.all_fields:
            if hasattr(field, 'on_resource_ready'):
                field.on_resource_ready()

        if abstract:
            return new_class

        # Register resource
        registration.register_resources(new_class)

        # Because of the way imports happen (recursively), we may or may not be
        # the first time this model tries to register with the framework. There
        # should only be one class for each model, so we always return the
        # registered version.
        return registration.get_resource(new_meta.resource_name)

    def add_to_class(cls, name, value):
        if hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)


class ResourceBase(object):
    def __init__(self, *args, **kwargs):
        args_len = len(args)
        meta = getmeta(self)
        if args_len > len(meta.fields):
            raise TypeError('This resource takes %s positional arguments but %s where given.' % (
                len(meta.fields), args_len))

        # The ordering of the zip calls matter - zip throws StopIteration
        # when an iter throws it. So if the first iter throws it, the second
        # is *not* consumed. We rely on this, so don't change the order
        # without changing the logic.
        fields_iter = iter(meta.fields)
        if args_len:
            if not kwargs:
                for val, field in zip(args, fields_iter):
                    setattr(self, field.attname, val)
            else:
                for val, field in zip(args, fields_iter):
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
            raise TypeError("'%s' is an invalid keyword argument for this function" % list(kwargs)[0])

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self)

    def __str__(self):
        return '%s resource' % getmeta(self).resource_name

    @classmethod
    def create_from_dict(cls, d, full_clean=False):
        """
        Create a resource instance from a dictionary.
        """
        return create_resource_from_dict(d, cls, full_clean)

    def to_dict(self, include_virtual=True):
        """
        Convert this resource into a `dict` of field_name/value pairs.

        .. note::
            This method is not recursive, it only operates on this single resource, any sub resources are returned as
            is. The use case that prompted the creation of this method is within codecs when a resource must be
            converted into a type that can be serialised, these codecs then operate recursively on the returned `dict`.

        :param include_virtual: Include virtual fields when generating `dict`.

        """
        meta = getmeta(self)
        fields = meta.all_fields if include_virtual else meta.fields
        return dict((f.name, v) for f, v in field_iter_items(self, fields))

    def convert_to(self, to_resource, context=None, ignore_fields=None, **field_values):
        """
        Convert this resource into a specified resource.

        A mapping must be defined for conversion between this resource and to_resource or an exception will be raised.

        """
        mapping = registration.get_mapping(self.__class__, to_resource)
        ignore_fields = ignore_fields or []
        ignore_fields.extend(mapping.exclude_fields)
        self.full_clean(ignore_fields)
        return mapping(self, context).convert(**field_values)

    def update_existing(self, dest_obj, context=None, ignore_fields=None):
        """
        Update the fields on an existing destination object.

        A mapping must be defined for conversion between this resource and ``dest_obj`` type or an exception will be
        raised.

        """
        self.full_clean(ignore_fields)
        mapping = registration.get_mapping(self.__class__, dest_obj.__class__)
        return mapping(self, context).update(dest_obj, ignore_fields)

    def extra_attrs(self, attrs):
        """
        Called during de-serialisation of data if there are any extra fields defined in the document.

        This allows the resource to decide how to handle these fields. By default they are ignored.
        """
        pass

    def clean(self):
        """
        Chance to do more in depth validation.
        """
        pass

    def full_clean(self, exclude=None):
        """
        Calls clean_fields, clean on the resource and raises ``ValidationError``
        for any errors that occurred.
        """
        errors = {}

        try:
            self.clean_fields(exclude)
        except ValidationError as e:
            errors = e.update_error_dict(errors)

        try:
            self.clean()
        except ValidationError as e:
            errors = e.update_error_dict(errors)

        if errors:
            raise ValidationError(errors)

    def clean_fields(self, exclude=None):
        errors = {}

        for f in getmeta(self).fields:
            if exclude and f.name in exclude:
                continue

            raw_value = f.value_from_object(self)

            if f.null and raw_value is None:
                continue

            try:
                raw_value = f.clean(raw_value)
            except ValidationError as e:
                errors[f.name] = e.messages

            # Check for resource level clean methods.
            clean_method = getattr(self, "clean_%s" % f.attname, None)
            if callable(clean_method):
                try:
                    raw_value = clean_method(raw_value)
                except ValidationError as e:
                    errors.setdefault(f.name, []).extend(e.messages)

            setattr(self, f.attname, raw_value)

        if errors:
            raise ValidationError(errors)


@six.add_metaclass(ResourceType)
class Resource(ResourceBase):
    pass


def resolve_resource_type(resource):
    if isinstance(resource, type) and issubclass(resource, ResourceBase):
        meta = getmeta(resource)
        return meta.resource_name, meta.type_field
    else:
        return resource, DEFAULT_TYPE_FIELD


def create_resource_from_iter(i, resource, full_clean=True, default_to_not_provided=False):
    """
    Create a resource from an iterable sequence

    :param i: Iterable of values (it is assumed the values are in field order)
    :param resource: A resource type, resource name or list of resources and names to use as the base for creating a
        resource.
    :param full_clean: Perform a full clean as part of the creation, this is useful for parsing data with known
        columns (eg CSV data).
    :param default_to_not_provided: If an value is not supplied keep the value as NOT_PROVIDED. This is used
        to support merging an updated value.
    :return: New instance of resource type specified in the *resource* param.

    """
    i = list(i)
    resource_type = resource
    fields = getmeta(resource_type).fields

    # Optimisation to allow the assumption that len(fields) == len(i)
    extra = []
    if len(i) < len(fields):
        i += [NOT_PROVIDED] * (len(fields) - len(i))
    elif len(i) > len(fields):
        i = i[:len(fields)]
        extra = i[len(fields):]

    attrs = []
    errors = {}
    for f, value in zip(fields, i):
        if value is NOT_PROVIDED:
            if not default_to_not_provided:
                value = f.get_default() if f.use_default_if_not_provided else None
        else:
            try:
                value = f.to_python(value)
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


def create_resource_from_dict(d, resource=None, full_clean=True, copy_dict=True, default_to_not_provided=False):
    """
    Create a resource from a dict.

    :param d: dictionary of data.
    :param resource: A resource type, resource name or list of resources and names to use as the base for creating a
        resource. If a list is supplied the first item will be used if a resource type is not supplied; this could also
        be a parent(s) of any resource defined by the dict.
    :param full_clean: Perform a full clean as part of the creation.
    :param copy_dict: Use a copy of the input dictionary rather than destructively processing the input dict.
    :param default_to_not_provided: If an value is not supplied keep the value as NOT_PROVIDED. This is used
        to support merging an updated value.

    """
    assert isinstance(d, dict)

    if copy_dict:
        d = d.copy()

    if resource:
        resource_type = None

        # Convert to single resource then resolve document type
        if isinstance(resource, (tuple, list)):
            resources = (resolve_resource_type(r) for r in resource)
        else:
            resources = [resolve_resource_type(resource)]

        for resource_name, type_field in resources:
            # See if the input includes a type field  and check it's registered
            document_resource_name = d.get(type_field, None)
            if document_resource_name:
                resource_type = registration.get_resource(document_resource_name)
            else:
                resource_type = registration.get_resource(resource_name)

            if not resource_type:
                raise exceptions.ResourceException("Resource `%s` is not registered." % document_resource_name)

            if document_resource_name:
                # Check resource types match or are inherited types
                if (resource_name == document_resource_name or
                        resource_name in getmeta(resource_type).parent_resource_names):
                    break  # We are done
            else:
                break

        if not resource_type:
            raise exceptions.ResourceException(
                "Incoming resource does not match [%s]" % ', '.join(r for r, t in resources))
    else:
        # No resource specified, relay on type field
        document_resource_name = d.pop(DEFAULT_TYPE_FIELD, None)
        if not document_resource_name:
            raise exceptions.ResourceException("Resource not defined.")

        # Get an instance of a resource type
        resource_type = registration.get_resource(document_resource_name)
        if not resource_type:
            raise exceptions.ResourceException("Resource `%s` is not registered." % document_resource_name)

    attrs = []
    errors = {}
    for f in getmeta(resource_type).fields:
        value = d.pop(f.name, NOT_PROVIDED)
        if value is NOT_PROVIDED:
            if not default_to_not_provided:
                value = f.get_default() if f.use_default_if_not_provided else None
        else:
            try:
                value = f.to_python(value)
            except ValidationError as ve:
                errors[f.name] = ve.error_messages
        attrs.append(value)

    if errors:
        raise ValidationError(errors)

    new_resource = resource_type(*attrs)
    if d:
        new_resource.extra_attrs(d)
    if full_clean:
        new_resource.full_clean()
    return new_resource


def build_object_graph(d, resource=None, full_clean=True, copy_dict=True, default_to_not_supplied=False):
    """
    Generate an object graph from a dict

    :param d: Dictionary to build from
    :param resource: A resource type, resource name or list of resources and names to use as the base for creating a
        resource. If a list is supplied the first item will be used if a resource type is not supplied.
    :param full_clean: Perform a full clean once built; default is True
    :param copy_dict: Clone the dict before doing build; default is True
    :param default_to_not_supplied: If an value is not supplied keep the value as NOT_PROVIDED. This is used
        to support merging an updated value.
    :raises ValidationError: During building of the object graph and issues discovered are raised as a ValidationError.

    """
    if isinstance(d, dict):
        return create_resource_from_dict(d, resource, full_clean, copy_dict, default_to_not_supplied)

    if isinstance(d, list):
        return [build_object_graph(o, resource, full_clean, copy_dict, default_to_not_supplied) for o in d]

    return d


class ResourceIterable(bases.ResourceIterable):
    """
    Iterable that yields resources.
    """
    def __init__(self, sequence):
        self.sequence = sequence

    def __iter__(self):
        for item in self.sequence:
            yield item
