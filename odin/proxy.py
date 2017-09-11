import six

from odin.fields import NOT_PROVIDED
from odin.utils import getmeta


class FieldProxyDescriptor(object):
    """
    Descriptor to proxy field to underlying resource.
    """
    __slots__ = ('resource', 'name')

    def __init__(self, resource, name):
        self.resource = resource
        self.name = name

    def __get__(self, instance, owner):
        return getattr(self.resource, self.name)

    def __set__(self, instance, value):
        return setattr(self.resource, self.name, value)


class ResourceProxyOptions(object):
    META_OPTION_NAMES = (
        'resource', 'include', 'exclude', 'readonly',
        # Overrides
        'name', 'namespace', 'name_space', 'verbose_name', 'verbose_name_plural', 'doc_group',
        'field_sorting',
    )

    def __init__(self, meta):
        self.meta = meta
        self.resource = None
        self.fields = []
        self.include = []
        self.exclude = []
        self.readonly = []

        self.name = None
        self.name_space = NOT_PROVIDED
        self.verbose_name = None
        self.verbose_name_plural = None
        self.doc_group = None
        self.field_sorting = False

    def __repr__(self):
        return '<ProxyOptions for {}>'.format()

    def contribute_to_class(self, cls, _):
        cls._meta = self
        self.name = cls.__name__
        self.class_name = "{}.{}".format(cls.__module__, cls.__name__)

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

        base_meta = getmeta(meta.resource)

        # Determine which fields are included
        fields = set(base_meta.field_map)
        include = set(new_meta.include)
        if include:
            fields.intersection_update(include)
        exclude = set(new_meta.exclude)
        if exclude:
            fields.difference_update(exclude)

        # Identify readonly fields
        readonly = set(new_meta.readonly)
        if readonly:
            readonly.intersection_update(fields)

        new_meta.fields = fields

        return new_class

    def add_to_class(cls, name, value):
        if hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)


class ResourceProxyBase(object):
    @classmethod
    def proxy(cls, resource, *args, **kwargs):
        kwargs['__resource'] = resource
        return cls(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        self.resource = kwargs.pop('__resource', None)


class ResourceProxy(six.with_metaclass(ResourceProxyType, ResourceProxyBase)):
    pass


if __name__ == '__main__':
    import odin


    class Sample(odin.Resource):
        name = odin.StringField()
        year = odin.IntegerField()


    class SampleProxy(ResourceProxy):
        class Meta:
            resource = Sample
            exclude = ['name']

    pass
