"""
Resource Proxy
~~~~~~~~~~~~~~

The resource proxy is an object that provides an alternate interface to a shadowed Resource.

This could be as a means of providing a summary object, or for adding additional properties.

"""

import six

# Typing includes
from typing import List, Union  # noqa

from odin import registration

from odin.bases import TypedResourceIterable
from odin.resources import ResourceOptions, ResourceBase
from odin.utils import getmeta, filter_fields, lazy_property

EMPTY = tuple()


class FieldProxyDescriptor(object):
    """
    Descriptor to proxy field to underlying resource.
    """
    __slots__ = ('attname', 'readonly')

    def __init__(self, readonly=False):
        self.attname = None  # type: str
        self.readonly = readonly

    def __get__(self, instance, owner):
        shadow = getattr(instance, '_shadow')
        return getattr(shadow, self.attname)

    def __set__(self, instance, value):
        if self.readonly:
            raise AttributeError("can't set attribute")
        shadow = getattr(instance, '_shadow')
        return setattr(shadow, self.attname, value)

    def contribute_to_class(self, cls, name):
        self.attname = name
        setattr(cls, name, self)


class ResourceProxyOptions(ResourceOptions):
    META_OPTION_NAMES = (
        'include', 'exclude', 'readonly',
        # Overrides
        'name', 'name_space', 'namespace', 'verbose_name', 'verbose_name_plural', 'doc_group',
        'type_field', 'key_field_name', 'key_field_names', 'field_sorting',
    )

    def __init__(self, meta):
        super(ResourceProxyOptions, self).__init__(meta)
        self.resource = None
        self.shadow = None
        self.include = []
        self.exclude = []
        self.readonly = []

    def __repr__(self):
        return '<Proxy of {!r}>'.format(getmeta(self.resource))

    def contribute_to_class(self, cls, _):
        cls._meta = self
        cls_name = cls.__name__
        self.name = cls_name
        self.class_name = "{}.{}".format(cls.__module__, cls_name)

        # Get and filter meta attributes
        meta_attrs = self.meta.__dict__.copy()
        for name in self.meta.__dict__:
            if name.startswith('_'):
                del meta_attrs[name]

        # Get the required resource object
        self.resource = meta_attrs.pop('resource', None)
        if not self.resource:
            raise AttributeError('`resource` has not been defined.')
        self.shadow = shadow = getmeta(self.resource)

        # Extract all meta options and fetch from shadow if not defined
        proxy_attrs = {
            'name': cls_name,
            'verbose_name': cls_name.replace('_', ' ').strip('_ '),
        }
        for attr_name in self.META_OPTION_NAMES:
            if attr_name in meta_attrs:
                value = meta_attrs.pop(attr_name)

                if attr_name == 'verbose_name':
                    # If defined generate pluralised form base on this name.
                    if 'verbose_name_plural' not in proxy_attrs:
                        proxy_attrs['verbose_name_plural'] = value + 's'

                elif attr_name == 'namespace':
                    # Allow meta to be defined as namespace
                    attr_name = 'name_space'

                elif attr_name == 'key_field_name':
                    # Remap to key_field names
                    attr_name = 'key_field_names'
                    value = [value]

                proxy_attrs[attr_name] = value

            elif hasattr(shadow, attr_name):
                proxy_attrs.setdefault(attr_name, getattr(shadow, attr_name))

        # Any leftover attributes must be invalid.
        if meta_attrs != {}:
            raise TypeError("'class Meta' got invalid attribute(s): %s" % ','.join(meta_attrs.keys()))
        del self.meta

        # Apply to self
        for attr_name, value in proxy_attrs.items():
            setattr(self, attr_name, value)

    @lazy_property
    def readonly_fields(self):
        """
        Fields that can only be read from.
        """
        return tuple(f for f in self.fields if f.attname in self.readonly)

    @lazy_property
    def init_fields(self):
        """
        Fields used in the resource init
        """
        return tuple(f for f in self.fields if f.attname not in self.readonly)


class ResourceProxyType(type):
    meta_options = ResourceProxyOptions

    def __new__(mcs, name, bases, attrs):
        super_new = super(ResourceProxyType, mcs).__new__

        # attrs will never be empty for classes declared in the standard way
        # (ie. with the `class` keyword). This is quite robust.
        if name == 'NewBase' and attrs == {}:
            return super_new(mcs, name, bases, attrs)

        parents = [
            b for b in bases if
            isinstance(b, ResourceProxyType) and not (b.__name__ == 'NewBase' and b.__mro__ == (b, object))
        ]
        if not parents:
            # If this isn't a subclass of Resource, don't do anything special.
            return super_new(mcs, name, bases, attrs)

        # Create the class.
        module = attrs.pop('__module__')
        new_class = super_new(mcs, name, bases, {'__module__': module})
        attr_meta = attrs.pop('Meta', None)
        if not attr_meta:
            meta = getattr(new_class, 'Meta', None)
        else:
            meta = attr_meta

        new_meta = mcs.meta_options(meta)
        new_class.add_to_class('_meta', new_meta)

        # Add all attributes to the class.
        for obj_name, obj in attrs.items():
            new_class.add_to_class(obj_name, obj)

        # Determine which fields will be shadowed.
        field_names, readonly = filter_fields(
            new_meta.shadow.field_map,
            new_meta.include,
            new_meta.exclude,
            new_meta.readonly
        )

        # Map field names
        new_meta.fields = [f for f in new_meta.shadow.fields if f.attname in field_names]

        # Sort the fields
        if new_meta.field_sorting:
            if callable(new_meta.field_sorting):
                new_meta.fields = new_meta.field_sorting(new_meta.fields)
            else:
                new_meta.fields = sorted(new_meta.fields, key=hash)

        # Generate field descriptors
        for field in new_meta.fields:
            new_class.add_to_class(field.attname, FieldProxyDescriptor(field in new_meta.readonly_fields))

        # If a key_field is defined ensure it exists
        if new_meta.key_field_names:
            for field_name in new_meta.key_field_names:
                if field_name not in new_meta.field_map:
                    raise AttributeError('Key field `{0}` is not exist on this resource.'.format(field_name))

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


class ResourceProxyIter(TypedResourceIterable):
    """
    Returned by `ResourceProxy.proxy` if an iterable is supplied.
    """
    def __init__(self, objects, resource_type):
        # type: (Union[List[ResourceBase]], ResourceProxyBase) -> None
        super(ResourceProxyIter, self).__init__(resource_type)
        self.objects = objects

    def __iter__(self):
        resource_type = self.resource_type
        for obj in self.objects:
            yield resource_type.proxy(obj)


class ResourceProxyBase(ResourceBase):
    """
    Base proxy class
    """
    @classmethod
    def proxy(cls, resource):
        if hasattr(resource, '__iter__'):
            return ResourceProxyIter(resource, cls)
        elif isinstance(resource, ResourceBase):
            return cls(__resource=resource)
        raise TypeError("Only resource types can be proxied.")

    def __init__(self, *args, **kwargs):
        meta = getmeta(self)

        # Get shadowed resource if supplied
        shadow = kwargs.pop('__resource', None)
        if shadow is None:
            # Create a new instance
            self._shadow = meta.resource()
            super(ResourceProxyBase, self).__init__(*args, **kwargs)
        else:
            self._shadow = shadow

    def get_shadow(self):
        return self._shadow


class ResourceProxy(six.with_metaclass(ResourceProxyType, ResourceProxyBase)):
    """
    Proxy for a Resources that allow a filtered set of fields to be made
    available and updated.
    """
