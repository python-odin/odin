# -*- coding: utf-8 -*-
import six

META_OPTION_NAMES = ()


class MappingOptions(object):
    pass


class MappingBase(type):
    """
    Metaclass for all Mappings
    """
    def __new__(cls, name, bases, attrs):
        pass


class Mapping(six.with_metaclass(MappingBase)):
    from_resource = None
    to_resource = None
    exclude_fields = []
    include_fields = None
