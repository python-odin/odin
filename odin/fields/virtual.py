# -*- coding: utf-8 -*-


class VirtualField(object):
    """
    Base class for virtual fields. A virtual fields is treated like any other field during encoding/decoding (provided
    it can be written to).
    """
    # These track each time a VirtualField instance is created. Used to retain order.
    creation_counter = 0
    data_type_name = None

    def __init__(self, verbose_name=None, verbose_name_plural=None, name=None, data_type_name=None, doc_text=''):
        """
        Initialisation of virtual field

        :param verbose_name: Display name of field.
        :param verbose_name_plural: Plural display name of field.
        :param name: Name of the serialised field.
        :param data_type_name: A name for the data type this field returns (used for generating documentation)
        :param doc_text: Documentation for the field, replaces help text
        """
        self.verbose_name, self.verbose_name_plural = verbose_name, verbose_name_plural
        self.name = name
        self.doc_text = doc_text
        self.data_type_name = data_type_name

        self.creation_counter = VirtualField.creation_counter
        VirtualField.creation_counter += 1

    def __hash__(self):
        return self.creation_counter

    def __get__(self, instance, owner):
        raise NotImplementedError

    def __set__(self, instance, value):
        raise AttributeError("Read only")

    def __repr__(self):
        """
        Displays the module, class and name of the field.
        """
        path = '%s.%s' % (self.__class__.__module__, self.__class__.__name__)
        name = getattr(self, 'name', None)
        if name is not None:
            return '<%s: %s>' % (path, name)
        return '<%s>' % path

    def set_attributes_from_name(self, attname):
        if not self.name:
            self.name = attname
        self.attname = attname
        if self.verbose_name is None and self.name:
            self.verbose_name = self.name.replace('_', ' ')
        if self.verbose_name_plural is None and self.verbose_name:
            self.verbose_name_plural = "%ss" % self.verbose_name

    def contribute_to_class(self, cls, name):
        self.set_attributes_from_name(name)
        self.resource = cls
        cls._meta.add_virtual_field(self)

        setattr(cls, name, self)

    def prepare(self, value):
        """
        Prepare a value for serialisation.

        :param value:
        :return:
        """
        return value

    def value_from_object(self, obj):
        """
        Returns the value of this field in the given resource instance.
        """
        return getattr(obj, self.attname)


class ConstantField(VirtualField):
    """
    A field that provides a constant value.
    """
    def __init__(self, value, *args, **kwargs):
        super(ConstantField, self).__init__(*args, **kwargs)
        self.value = value

    def __get__(self, instance, owner):
        return self.value


class CalculatedField(VirtualField):
    """
    A field whose that is calculated by an expression.

    The expression should accept a single "self" parameter that is a Resource instance.
    """
    def __init__(self, expr, *args, **kwargs):
        assert callable(expr)
        super(CalculatedField, self).__init__(*args, **kwargs)
        self.expr = expr

    def __get__(self, instance, owner):
        return self.expr(instance)


def calculated_field(method=None, **kwargs):
    """
    Converts an instance method into a calculated field.
    """
    def inner(expr):
        return CalculatedField(expr, **kwargs)
    return inner if method is None else inner(method)
