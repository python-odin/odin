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
    def repl(match_obj):
        return sep + match_obj.group(0).lower()
    return _CAMEL_CASE_RE.sub(repl, s).strip(sep)


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
    def repl(match_obj):
        return match_obj.group(1).upper()
    return _LOWER_UNDERSCORE_CASE_RE.sub(repl, value.lower())


def lower_dash_to_camel(value):
    """
    Convert lower dash case to camel case

      background-color -> backgroundColor
    """
    def repl(match_obj):
        return match_obj.group(1).upper()
    return _LOWER_DASH_CASE_RE.sub(repl, value.lower())
