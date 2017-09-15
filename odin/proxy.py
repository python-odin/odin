import six

# Typing includes
from typing import List, Dict, Tuple  # noqa
from odin.fields import Field  # noqa

from odin.fields import NOT_PROVIDED
from odin.resources import ResourceBase, DEFAULT_TYPE_FIELD
from odin.utils import getmeta

EMPTY = tuple()


class FieldProxyDescriptor(object):
    """
    Descriptor to proxy field to underlying resource.
    """
    __slots__ = ('attname',)

    def __init__(self):
        self.attname = None  # type: str

    def __get__(self, instance, owner):
        shadow = getattr(instance, '_shadow')
        return getattr(shadow, self.attname)

    def __set__(self, instance, value):
        shadow = getattr(instance, '_shadow')
        return setattr(shadow, self.attname, value)

    def contribute_to_class(self, cls, name):
        self.attname = name
        setattr(cls, name, self)


def filter_fields(field_map, include=None, exclude=None, readonly=None):
    # type: (Dict[str, Field], List[str], List[str], List[str]) -> Tuple[List[Field], List[Field]]
    """
    Filter a field list using the include/exclude options
    """
    fields = set(field_map)

    include = set(include or EMPTY)
    if include:
        fields.intersection_update(include)

    exclude = set(exclude or EMPTY)
    if exclude:
        fields.difference_update(exclude)

    readonly = set(readonly or EMPTY)
    if readonly:
        readonly.intersection_update(fields)

    return (
        sorted((field_map[f] for f in fields), key=hash),
        sorted((field_map[f] for f in readonly), key=hash)
    )


class ResourceProxyOptions(object):
    META_OPTION_NAMES = (
        'include', 'exclude', 'readonly',
        # Overrides
        'name', 'namespace', 'name_space', 'verbose_name', 'verbose_name_plural', 'doc_group',
        'type_field', 'key_field_name', 'key_field_names', 'field_sorting'
    )

    def __init__(self, meta):
        self.meta = meta
        self.resource = None
        self.shadow = None
        self.include = []
        self.exclude = []
        self.readonly = []

        self.fields = []
        self._key_fields = []
        self.virtual_fields = []

        self.name = None
        self.class_name = None
        self.name_space = NOT_PROVIDED
        self.verbose_name = None
        self.verbose_name_plural = None
        self.doc_group = None
        self.type_field = DEFAULT_TYPE_FIELD
        self.key_field_names = None
        self.field_sorting = False

    def __repr__(self):
        return '<Proxy of {!r}>'.format(getmeta(self.resource))

    def contribute_to_class(self, cls, _):
        cls._meta = self
        self.name = cls.__name__
        self.class_name = "{}.{}".format(cls.__module__, cls.__name__)

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
        for attr_name in self.META_OPTION_NAMES:
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

        if not new_meta.resource:
            raise AttributeError("'resource' meta option not defined.")

        # Determine which fields will be shadowed.
        base_meta = getmeta(meta.resource)
        fields, readonly = filter_fields(
            base_meta.field_map,
            new_meta.include,
            new_meta.exclude,
            new_meta.readonly
        )

        # Generate field descriptors
        for field in fields:
            new_class.add_to_class(field.attname, FieldProxyDescriptor())

        new_meta.fields = fields

        return new_class

    def add_to_class(cls, name, value):
        if hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)


class ResourceProxyBase(ResourceBase):
    """
    Base proxy class
    """
    @classmethod
    def proxy(cls, resource):
        return cls(__resource=resource)

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
