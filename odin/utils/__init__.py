# -*- coding: utf-8 -*-
import re

# Typing imports
from typing import Iterable, Tuple, Union, Set, T  # noqa

_CAMEL_CASE_RE = re.compile(r'[A-Z]')
_LOWER_UNDERSCORE_CASE_RE = re.compile(r'_([a-z])')
_LOWER_DASH_CASE_RE = re.compile(r'-([a-z])')


def camel_to_lower_separated(s, sep):
    # type: (str, str) -> str
    """
    Convert camel case representation into lower separated case ie:

      backgroundColor -> background_color

    Note any separator at the start or end is stripped.

    """
    return _CAMEL_CASE_RE.sub(lambda m: sep + m.group(0).lower(), s).strip(sep)


def camel_to_lower_underscore(s):
    # type: (str) -> str
    """
    Convert camel case to lower underscore case.

        backgroundColor -> background_color

    """
    return camel_to_lower_separated(s, '_')


def camel_to_lower_dash(s):
    # type: (str) -> str
    """
    Convert camel case to lower dash case.

      backgroundColor -> background-color
    """
    return camel_to_lower_separated(s, '-')


def lower_underscore_to_camel(value):
    # type: (str) -> str
    """
    Convert lower underscore case to camel case

      background_color -> backgroundColor

    """
    return _LOWER_UNDERSCORE_CASE_RE.sub(
        lambda m: m.group(1).upper(),
        value.lower()
    )


def lower_dash_to_camel(value):
    # type: (str) -> str
    """
    Convert lower dash case to camel case

      background-color -> backgroundColor

    """
    return _LOWER_DASH_CASE_RE.sub(
        lambda m: m.group(1).upper(),
        value.lower()
    )


class cached_property(object):  # noqa - Made to match property builtin
    """
    Acts like a standard class `property` except return values cached.
    """
    @staticmethod
    def clear_caches(instance):
        instance._cache = {}

    def __init__(self, func):
        self.func = func
        self.__doc__ = func.__doc__
        self.__name__ = func.__name__
        self.__module__ = func.__module__

    def __get__(self, instance, owner):
        try:
            value = instance._cache[self.__name__]
        except (KeyError, AttributeError):
            value = self.func(instance)
            try:
                cache = instance._cache
            except AttributeError:
                cache = instance._cache = {}
            cache[self.__name__] = value
        return value


class lazy_property(object):  # noqa - Made to match the property builtin
    """
    The bottle cached property, requires a alternate name so as not to
    clash with existing cached_property behaviour
    """
    def __init__(self, func):
        self.func = func
        self.__doc__ = func.__doc__

    def __get__(self, instance, owner):
        if instance is None:
            return self
        value = instance.__dict__[self.func.__name__] = self.func(instance)
        return value


EMPTY = []


def filter_fields(field_names, include=None, exclude=None, readonly=None):
    # type: (Iterable[str], Iterable[str], Iterable[str], Iterable[str]) -> Tuple[Set[str], Set[str]]
    """
    Filter a field iterable using the include/exclude/readonly options

    :param field_names: Iterable of field names as the source list
    :param include: Iterable of field names to be included
    :param exclude: Iterable of field names to be excluded
    :param readonly: Iterable of field names to be treated as read-only.
    :returns: A pair of sets of field names, the first is the set that have been selected,
        the second item is a set that have been selected and indicated to as read-only.
    
    """
    field_names = set(field_names)

    include = set(include or EMPTY)
    if include:
        field_names.intersection_update(include)

    exclude = set(exclude or EMPTY)
    if exclude:
        field_names.difference_update(exclude)

    readonly = set(readonly or EMPTY)
    if readonly:
        readonly.intersection_update(field_names)

    return field_names, readonly


def getmeta(resource_or_instance):
    """
    Get meta object from a resource or resource instance.

    :param resource_or_instance: Resource or instance of a resource.
    :type resource_or_instance: odin.resources.ResourceType | odin.resources.ResourceBase
    :return: Meta options class
    :rtype: odin.resources.ResourceOptions

    """
    return getattr(resource_or_instance, '_meta')


def field_iter(resource, include_virtual=True):
    """
    Return an iterator that yields fields from a resource.

    :param resource: Resource to iterate over.
    :param include_virtual: Include virtual fields.
    :returns: an iterator that returns fields.

    """
    meta = getmeta(resource)
    if include_virtual:
        return iter(meta.all_fields)
    else:
        return iter(meta.fields)


def field_iter_items(resource, fields=None):
    """
    Return an iterator that yields fields and their values from a resource.

    :param resource: Resource to iterate over.
    :param fields: Fields to use; if :const:`None` defaults to all of the resources fields.
    :returns: an iterator that returns (field, value) tuples.

    """
    meta = getmeta(resource)
    if fields is None:
        fields = meta.all_fields
    for f in fields:
        yield f, f.prepare(f.value_from_object(resource))


def virtual_field_iter_items(resource):
    """
    Return an iterator that yields virtual fields and their values from a resource.

    :param resource: Resource to iterate over.
    :returns: an iterator that returns (field, value) tuples.

    """
    meta = getmeta(resource)
    return field_iter_items(resource, meta.virtual_fields)


def attribute_field_iter_items(resource):
    """
    Return an iterator that yields fields and their values from a resource that have the attribute flag set.

    :param resource: Resource to iterate over.
    :returns: an iterator that returns (field, value) tuples.

    :note::
        This iterator is designed for codecs that have a distinction between attribute and element fields (eg XML).

    """
    return field_iter_items(resource, getmeta(resource).attribute_fields)


def element_field_iter_items(resource):
    """
    Return an iterator that yields fields and their values from a resource that do not have the attribute flag set.

    :param resource: Resource to iterate over.
    :returns: an iterator that returns (field, value) tuples.

    :note::
        This iterator is designed for codecs that have a distinction between attribute and element fields (eg XML).

    """
    return field_iter_items(resource, getmeta(resource).element_fields)


def extract_fields_from_dict(d, resource):
    """
    Extract values from a dict that are defined on a resource.

    Fields that are not found will not be included in the output dict.

    :param d: the source dictionary.
    :param resource: the resource that provides the fields.
    :returns: a dictionary of the resource fields that where found in the dict.

    """
    return dict((f.name, d[f.name]) for f in field_iter(resource) if f.name in d)


def value_in_choices(value, choices):
    """
    Check if the value appears in the choices list (a iterable of tuples, the first value of which is the choice value)

    :param value:
    :param choices:
    :return: True if value is in the choices iterable.

    """
    for choice in choices:
        if value == choice[0]:
            return True
    return False


def iter_to_choices(i):
    # type: (Iterable[T]) -> tuple(Tuple[T, str])
    """
    Convert an iterator of strings (or types that can be converted to strings) and convert these into choice value
    pairs.
    """
    return tuple((v, str(v).title()) for v in i)


def force_tuple(value):
    # type: (Union[T, tuple(T), list(T)]) -> tuple(T)
    """
    Forces a value to be a tuple.

    Either by converting into a tuple (if is a list) or changing value to be a tuple.

    """
    if value is None:
        return tuple()
    if isinstance(value, tuple):
        return value
    if isinstance(value, list):
        return tuple(value)
    return value,


def chunk(iterable, n):
    # type: (Iterable[T], int) -> Iterable[Iterable[T]]
    """
    Return iterable of n items from an iterable.

    :param iterable: Iterable of items
    :param n: Size of iterable chunks to return.
    :return: Iterable chunk of input iterable

    """
    iterable = iter(iterable)
    state = {'continue': True}

    def inner():
        for _ in range(n):
            try:
                yield next(iterable)
            except StopIteration:
                state['continue'] = False

    while state['continue']:
        yield inner()
