# -*- coding: utf-8 -*-
import re

_CAMEL_CASE_RE = re.compile(r'[A-Z]')
_LOWER_UNDERSCORE_CASE_RE = re.compile(r'_([a-z])')
_LOWER_DASH_CASE_RE = re.compile(r'-([a-z])')


def camel_to_lower_separated(s, sep):
    """
    Convert camel case representation into lower separated case ie:

      backgroundColor -> background_color

    Note any separator at the start or end is stripped.

    """
    return _CAMEL_CASE_RE.sub(lambda m: sep + m.group(0).lower(), s).strip(sep)


def camel_to_lower_underscore(s):
    """
    Convert camel case to lower underscore case.

        backgroundColor -> background_color
    """
    return camel_to_lower_separated(s, '_')


def camel_to_lower_dash(s):
    """
    Convert camel case to lower dash case.

      backgroundColor -> background-color
    """
    return camel_to_lower_separated(s, '-')


def lower_underscore_to_camel(value):
    """
    Convert lower underscore case to camel case

      background_color -> backgroundColor
    """
    return _LOWER_UNDERSCORE_CASE_RE.sub(
        lambda m: m.group(1).upper(),
        value.lower()
    )


def lower_dash_to_camel(value):
    """
    Convert lower dash case to camel case

      background-color -> backgroundColor
    """
    return _LOWER_DASH_CASE_RE.sub(
        lambda m: m.group(1).upper(),
        value.lower()
    )


class cached_property(object):
    """
    Acts like a standard class `property` except return values cached.
    """
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
