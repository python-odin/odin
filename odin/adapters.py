# -*- coding: utf-8 -*-
from odin.utils import field_iter_items

__all__ = ('ResourceAdapter',)


class ResourceOptionsAdapter(object):
    """
    A lightweight wrapper for the *ResourceOptions* class that filters fields.
    """
    def __init__(self, options, include, exclude):
        self._wrapped = options
        self._include = include
        self._exclude = exclude

        self.parents = []
        self.fields = []

        self.name = options.name
        self.class_name = None
        self.name_space = NOT_PROVIDED
        self.verbose_name = None
        self.verbose_name_plural = None
        self.abstract = False
        self.doc_group = None
        self.type_field = DEFAULT_TYPE_FIELD

    @property
    def field_map(self):
        return self._wrapped.field_map

    @property
    def resource_name(self):
        """
        Full name of resource including namespace (if specified)
        """
        return self._wrapped.resource_name

    @property
    def parent_resource_names(self):
        """
        List of parent resource names.
        """
        return self._wrapped.resource_name

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

    def __repr__(self):
        return '<Options Adapter for %s>' % self.resource_name


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
        self._source = source
        self._meta = ResourceOptionsAdapter(source._meta, include, exclude)

    def __getattr__(self, item):
        return getattr(self._source, item)

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self)

    def __str__(self):
        return '%s resource' % self._meta.resource_name

    def __iter__(self):
        """
        Iterate over a resource, returning field/value pairs.
        """
        return field_iter_items(self)

    def to_dict(self):
        """
        Convert this resource into a dict
        """
        return dict((f.name, v) for f, v in self)

    def full_clean(self):
        """
        Calls full_clean on wrapped resource and raises ``ValidationError``
        for any errors that occurred.
        """
        self._source.full_clean()
