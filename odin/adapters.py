# -*- coding: utf-8 -*-
from odin.utils import cached_property, field_iter_items

__all__ = ('ResourceAdapter',)


class CurriedAdapter(object):
    """
    Curry wrapper for a Adapter to allow for pre-config of include/exclude and
    any other user defined arguments provided in kwargs.
    """
    def __init__(self, cls, **kwargs):
        self.cls = cls
        self.kwargs = kwargs.copy()

    def __call__(self, source):
        return self.cls(source, **self.kwargs)

    def apply_to(self, sources):
        return self.cls.apply_to(sources, **self.kwargs)


class ResourceOptionsAdapter(object):
    """
    A lightweight wrapper for the *ResourceOptions* class that filters fields.
    """
    def __init__(self, options, include, exclude):
        self._wrapped = options
        self.parents = options.parents

        # Filter available fields
        include = include or [f.attname for f in options.all_fields]
        exclude = exclude or []
        self.fields = [f for f in options.fields if f.attname in include and f.attname not in exclude]
        self.virtual_fields = [f for f in options.virtual_fields if f.attname in include and f.attname not in exclude]

        # Work around so cached properties still work.
        self._cache = {}

    def __getattr__(self, item):
        return getattr(self._wrapped, item)

    def __repr__(self):
        return '<Options Adapter for %s>' % self.resource_name

    @cached_property
    def all_fields(self):
        """
        All fields both standard and virtual.
        """
        return self.fields + self.virtual_fields

    @cached_property
    def field_map(self):
        return dict((f.attname, f) for f in self.fields)

    @property
    def attribute_fields(self):
        """
        List of fields where is_attribute is True.
        """
        return [f for f in self.fields if f.is_attribute]

    @property
    def element_fields(self):
        """
        List of fields where is_attribute is False.
        """
        return [f for f in self.fields if not f.is_attribute]


class ResourceAdapter(object):
    """
    A lightweight wrapper that can be placed around a resource to filter out specific
    fields or to provide additional specific methods or calculated properties.

    A good use case for an adapter is an API where you wish to filter out certain fields
    or in a UI where you wish to add methods for rendering objects without extending the
    underlying resource that may be shared between multiple rendering engines or other
    subsystems.

    The *ResourceAdapter* can be passed to Odin codecs just like a *Resource*.

    """
    @classmethod
    def apply_to(cls, sources, include=None, exclude=None, **kwargs):
        """
        Convenience method that applies include/exclude lists to all items in an
        iterable collection of resources.

        :param sources: Source resources being wrapped.
        :param include: Fields that should be explicitly included on the adapter.
        :param exclude: Fields to explicitly exclude on the adapter.

        """
        meta_objects = {}
        for resource in sources:
            try:
                meta = meta_objects[resource._meta.resource_name]
            except KeyError:
                meta = cls._create_options_adapter(resource._meta, include, exclude)
                meta_objects[resource._meta.resource_name] = meta
            yield cls(resource, meta=meta, **kwargs)

    @classmethod
    def _create_options_adapter(cls, options, include=None, exclude=None):
        include_fields = include if include else getattr(cls, 'include_fields', None)
        exclude_fields = exclude if exclude else getattr(cls, 'exclude_fields', None)
        return ResourceOptionsAdapter(options, include_fields, exclude_fields)

    @classmethod
    def curry(cls, include=None, exclude=None, **kwargs):
        """
        Creates an Adapter that has include and exclude (and any other options) preset.

        :param include: Fields that should be explicitly included on the adapter.
        :param exclude: Fields to explicitly exclude on the adapter.
        :param kwargs:

        """
        return CurriedAdapter(cls, include=include, exclude=exclude, **kwargs)

    def __init__(self, source, include=None, exclude=None, meta=None):
        """
        Initialise the adapter.

        :param source: Source resource being wrapped.
        :param include: Fields that should be explicitly included on the adapter.
        :param exclude: Fields to explicitly exclude on the adapter.

        """
        self.__dict__['_source'] = source

        if not meta:
            meta = self._create_options_adapter(source._meta, include, exclude)
        self._meta = meta

    def __getattr__(self, item):
        return getattr(self._source, item)

    def __setattr__(self, name, value):
        setattr(self._source, name, value)

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self)

    def __str__(self):
        return '%s resource adapter' % self._meta.resource_name

    def to_dict(self, include_virtual=True):
        """
        Convert this resource into a dict
        """
        fields = self._meta.all_fields if include_virtual else self._meta.fields
        return dict((f.name, v) for f, v in field_iter_items(self, fields))
