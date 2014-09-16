# -*- coding: utf-8 -*-
import copy
import six
from odin import exceptions, registration
from odin.exceptions import ValidationError
from odin.fields import NOT_PROVIDED
from odin.utils import cached_property, field_iter_items


DEFAULT_TYPE_FIELD = '$'
META_OPTION_NAMES = (
    'name', 'namespace', 'name_space', 'verbose_name', 'verbose_name_plural', 'abstract', 'doc_group', 'type_field'
)


class ResourceOptions(object):
    def __init__(self, meta):
        self.meta = meta
        self.parents = []
        self.fields = []
        self.virtual_fields = []

        self.name = None
        self.class_name = None
        self.name_space = NOT_PROVIDED
        self.verbose_name = None
        self.verbose_name_plural = None
        self.abstract = False
        self.doc_group = None
        self.type_field = DEFAULT_TYPE_FIELD

        self._cache = {}

    def contribute_to_class(self, cls, name):
        cls._meta = self
        self.name = cls.__name__
        self.class_name = "%s.%s" % (cls.__module__, cls.__name__)

        if self.meta:
            meta_attrs = self.meta.__dict__.copy()
            for name in self.meta.__dict__:
                if name.startswith('_'):
                    del meta_attrs[name]
            for attr_name in META_OPTION_NAMES:
                if attr_name in meta_attrs:
                    # Allow meta to be defined as namespace
                    if attr_name == 'namespace':
                        setattr(self, 'name_space', meta_attrs.pop(attr_name))
                    else:
                        setattr(self, attr_name, meta_attrs.pop(attr_name))
                elif hasattr(self.meta, attr_name):
                    setattr(self, attr_name, getattr(self.meta, attr_name))

            # Any leftover attributes must be invalid.
            if meta_attrs != {}:
                raise TypeError("'class Meta' got invalid attribute(s): %s" % ','.join(meta_attrs.keys()))
        del self.meta

        if not self.verbose_name:
            self.verbose_name = self.name.replace('_', ' ').strip('_ ')
        if not self.verbose_name_plural:
            self.verbose_name_plural = self.verbose_name + 's'

    def add_field(self, field):
        self.fields.append(field)
        cached_property.clear_caches(self)

    def add_virtual_field(self, field):
        self.virtual_fields.append(field)
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
    def field_map(self):
        return {f.attname: f for f in self.fields}

    @cached_property
    def parent_resource_names(self):
        """
        List of parent resource names.
        """
        return [p._meta.resource_name for p in self.parents]

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

    def __repr__(self):
        return '<Options for %s>' % self.resource_name


class ResourceBase(type):
    """
    Metaclass for all Resources.
    """
    def __new__(cls, name, bases, attrs):
        super_new = super(ResourceBase, cls).__new__

        # attrs will never be empty for classes declared in the standard way
        # (ie. with the `class` keyword). This is quite robust.
        if name == 'NewBase' and attrs == {}:
            return super_new(cls, name, bases, attrs)

        parents = [b for b in bases if isinstance(b, ResourceBase) and not (b.__name__ == 'NewBase'
                                                                            and b.__mro__ == (b, object))]
        if not parents:
            # If this isn't a subclass of Resource, don't do anything special.
            return super_new(cls, name, bases, attrs)

        # Create the class.
        module = attrs.pop('__module__')
        new_class = super_new(cls, name, bases, {'__module__': module})
        attr_meta = attrs.pop('Meta', None)
        abstract = getattr(attr_meta, 'abstract', False)
        if not attr_meta:
            meta = getattr(new_class, 'Meta', None)
        else:
            meta = attr_meta
        base_meta = getattr(new_class, '_meta', None)

        new_class.add_to_class('_meta', ResourceOptions(meta))

        # Generate a namespace if one is not provided
        if new_class._meta.name_space is NOT_PROVIDED and base_meta:
            # Namespace is inherited
            if (not new_class._meta.name_space) or (new_class._meta.name_space is NOT_PROVIDED):
                new_class._meta.name_space = base_meta.name_space

        if new_class._meta.name_space is NOT_PROVIDED:
            new_class._meta.name_space = module

        # Bail out early if we have already created this class.
        r = registration.get_resource(new_class._meta.resource_name)
        if r is not None:
            return r

        # Add all attributes to the class.
        for obj_name, obj in attrs.items():
            new_class.add_to_class(obj_name, obj)

        # Sort the fields
        new_class._meta.fields = sorted(new_class._meta.fields, key=hash)

        # All the fields of any type declared on this model
        local_field_attnames = set([f.attname for f in new_class._meta.fields])
        field_attnames = set(local_field_attnames)

        for base in parents:
            if not hasattr(base, '_meta'):
                # Things without _meta aren't functional models, so they're
                # uninteresting parents.
                continue

            # Check for clashes between locally declared fields and those
            # on the base classes (we cannot handle shadowed fields at the
            # moment).
            for field in base._meta.all_fields:
                if field.attname in local_field_attnames:
                    raise Exception('Local field %r in class %r clashes with field of similar name from '
                                    'base class %r' % (field.attname, name, base.__name__))
            for field in base._meta.fields:
                if field.attname not in field_attnames:
                    field_attnames.add(field.attname)
                    new_class.add_to_class(field.attname, copy.deepcopy(field))
            for field in base._meta.virtual_fields:
                new_class.add_to_class(field.attname, copy.deepcopy(field))

            new_class._meta.parents += base._meta.parents
            new_class._meta.parents.append(base)

        if abstract:
            return new_class

        # Register resource
        registration.register_resources(new_class)

        # Because of the way imports happen (recursively), we may or may not be
        # the first time this model tries to register with the framework. There
        # should only be one class for each model, so we always return the
        # registered version.
        return registration.get_resource(new_class._meta.resource_name)

    def add_to_class(cls, name, value):
        if hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)


@six.add_metaclass(ResourceBase)
class Resource(object):
    def __init__(self, *args, **kwargs):
        args_len = len(args)
        if args_len > len(self._meta.fields):
            raise TypeError('This resource takes %s positional arguments but %s where given.' % (
                len(self._meta.fields), args_len))

        # The ordering of the zip calls matter - zip throws StopIteration
        # when an iter throws it. So if the first iter throws it, the second
        # is *not* consumed. We rely on this, so don't change the order
        # without changing the logic.
        fields_iter = iter(self._meta.fields)
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
        return '%s resource' % self._meta.resource_name

    @classmethod
    def create_from_dict(cls, d, full_clean=False):
        """
        Create a resource instance from a dictionary.
        """
        return create_resource_from_dict(d, cls, full_clean)

    def to_dict(self, include_virtual=True):
        """
        Convert this resource into a dict.

        :param include_virtual: Include virtual fields when generating dict.

        """
        fields = self._meta.all_fields if include_virtual else self._meta.fields
        return dict((f.name, v) for f, v in field_iter_items(self, fields))

    def convert_to(self, to_resource, context=None, **field_values):
        """
        Convert this resource into a specified to resource.

        A mapping must be defined for conversion between this resource and to_resource or an exception will be raised.
        """
        self.full_clean()
        mapping = registration.get_mapping(self.__class__, to_resource)
        return mapping(self, context).convert(**field_values)

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

    def full_clean(self):
        """
        Calls clean_fields, clean on the resource and raises ``ValidationError``
        for any errors that occurred.
        """
        errors = {}

        try:
            self.clean_fields()
        except ValidationError as e:
            errors = e.update_error_dict(errors)

        try:
            self.clean()
        except ValidationError as e:
            errors = e.update_error_dict(errors)

        if errors:
            raise ValidationError(errors)

    def clean_fields(self):
        errors = {}

        for f in self._meta.fields:
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


def create_resource_from_dict(d, resource=None, full_clean=True, copy_dict=True):
    """
    Create a resource from a dict.

    :param d: dictionary of data.
    :param resource: A resource type of resource name that is expected in the dict; this could also be a parent
        of any resource defined by the dict.
    :param full_clean: Do a full clean as part of the creation.
    :param copy_dict: Use a copy of the input dictionary rather than destructively processing the input dict.

    """
    assert isinstance(d, dict)

    if copy_dict:
        d = d.copy()

    # Get the correct resource name
    if isinstance(resource, type) and issubclass(resource, Resource):
        resource_name = resource._meta.resource_name
        type_field = resource._meta.type_field
    else:
        resource_name = resource
        type_field = DEFAULT_TYPE_FIELD

    # Get the correct resource name
    document_resource_name = d.pop(type_field, resource_name)
    if not (document_resource_name or resource_name):
        raise exceptions.ValidationError("Resource not defined.")

    # Get an instance of a resource type
    resource_type = registration.get_resource(document_resource_name)
    if not resource_type:
        raise exceptions.ValidationError("Resource `%s` is not registered." % document_resource_name)

    # Check if we have an inherited type.
    if resource_name and not (resource_name == document_resource_name or
                              resource_name in resource_type._meta.parent_resource_names):
        raise exceptions.ValidationError(
            "Expected resource `%s` does not match resource defined in document `%s`." % (
                resource_name, document_resource_name))

    attrs = []
    errors = {}
    for f in resource_type._meta.fields:
        value = d.pop(f.name, NOT_PROVIDED)
        if value is NOT_PROVIDED:
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


def build_object_graph(d, resource=None, full_clean=True, copy_dict=True):
    """
    Generate an object graph from a dict

    :raises ValidationError: During building of the object graph and issues discovered are raised as a ValidationError.
    """

    if isinstance(d, dict):
        return create_resource_from_dict(d, resource, full_clean, copy_dict)

    if isinstance(d, list):
        return [build_object_graph(o, resource, full_clean, copy_dict) for o in d]

    return d
