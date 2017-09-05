import six


class ResourceProxyOptions(object):
    META_OPTION_NAMES = (
        'resource', 'readonly', 'include', 'exclude',
        # Overrides
        'name', 'namespace', 'name_space', 'verbose_name', 'verbose_name_plural', 'doc_group',
        'field_sorting',
    )

    def __init__(self, meta):
        self.meta = meta
        self.parents = []
        self.fields = []
        self._key_fields = []
        self.virtual_fields = []

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

        # Ensure resource is defined


class ResourceProxyType(type):
    meta_options = ResourceProxyOptions

    def __new__(mcs, name, bases, attrs):
        super_new = super(ResourceProxyType, mcs).__new__

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

        if not meta.resource:
            raise AttributeError("'resource' meta option not defined.")

        return new_class


class ResourceProxyBase(object):
    def __init__(self, resource):
        self.resource = resource

    def __getattr__(self, item):
        pass

    def __setattr__(self, item, value):
        pass


class ResourceProxy(six.with_metaclass(ResourceProxyType, ResourceProxyBase)):
    pass
