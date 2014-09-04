# -*- coding: utf-8 -*-
from odin.utils import cached_property, field_iter_items

__all__ = ('ResourceAdapter',)


class ResourceOptionsAdapter(object):
    """
    A lightweight wrapper for the *ResourceOptions* class that filters fields.
    """
    def __init__(self, options, include, exclude):
        self._wrapped = options
        self.parents = options.parents

        # Filter available fields
        include = include or [f.attname for f in options.fields]
        exclude = exclude or []
        self.fields = [f for f in options.fields if f.attname in include and f.attname not in exclude]

        # Work around so cached properties still work.
        self._cache = {}

    def __getattr__(self, item):
        return getattr(self._wrapped, item)

    def __repr__(self):
        return '<Options Adapter for %s>' % self.resource_name

    @cached_property
    def field_map(self):
        return {f.attname: f for f in self.fields}

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
    A lightweight wrapper that can be placed around a resource to filter out specific fields or to provide additional
    specific methods or calculated properties.

    A good use case for an adapter is an API where you wish to filter out certain fields or in a UI where you wish to
    add methods for rendering objects without extending the underlying resource that may be shared between multiple
    rendering engines or other subsystems.

    The *ResourceAdapter* can be passed to Odin codecs just like a *Resource*.

    """
    def __init__(self, source, include=None, exclude=None):
        """
        Initialise the adapter.

        :param source: Source resource being wrapped.
        :param include: Fields that should be explicitly included on the adapter.
        :param exclude: Fields to explicitly exclude on the adapter.
        """
        self.__dict__['_source'] = source

        include_fields = include if include else getattr(self, 'include_fields', None)
        exclude_fields = exclude if exclude else getattr(self, 'exclude_fields', None)

        self._meta = ResourceOptionsAdapter(source._meta, include_fields, exclude_fields)

    def __getattr__(self, item):
        return getattr(self._source, item)

    def __setattr__(self, name, value):
        setattr(self._source, name, value)

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self)

    def __str__(self):
        return '%s resource adapter' % self._meta.resource_name

    def to_dict(self):
        """
        Convert this resource into a dict
        """
        return dict((f.name, v) for f, v in field_iter_items(self))
