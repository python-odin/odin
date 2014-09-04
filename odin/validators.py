# -*- coding: utf-8 -*-
# This file is largely verbatim from the Django project, the wheel works well, no need to re-invent it.
#
# A note: to use validators from the Django project install the baldr package. Baldr is an integration between Odin and
# the Django framework, the integration includes support for handling the Django version of the ValidationError
# exception within Odin.
import re
import six
from odin import exceptions

EMPTY_VALUES = (None, '', [], (), {})


class RegexValidator(object):
    regex = ''
    message = 'Enter a valid value.'
    code = 'invalid'

    def __init__(self, regex=None, message=None, code=None):
        if regex is not None:
            self.regex = regex
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

        # Compile the regex if it was not passed pre-compiled.
        if isinstance(self.regex, six.string_types):
            self.regex = re.compile(self.regex)

    def __call__(self, value):
        """
        Validates that the input matches the regular expression.
        """
        if not self.regex.search(value):
            raise exceptions.ValidationError(self.message, code=self.code)


class URLValidator(RegexValidator):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    message = "Enter a valid URL value."

validate_url = URLValidator()


class BaseValidator(object):
    compare = lambda self, a, b: a is not b
    clean = lambda self, x: x
    message = 'Ensure this value is %(limit_value)s (it is %(show_value)s).'
    code = 'limit_value'

    def __init__(self, limit_value):
        self.limit_value = limit_value

    def __call__(self, value):
        cleaned = self.clean(value)
        params = {'limit_value': self.limit_value, 'show_value': cleaned}
        if self.compare(cleaned, self.limit_value):
            raise exceptions.ValidationError(self.message % params, code=self.code, params=params)


class MaxValueValidator(BaseValidator):
    compare = lambda self, a, b: a > b
    message = 'Ensure this value is less than or equal to %(limit_value)s.'
    code = 'max_value'


class MinValueValidator(BaseValidator):
    compare = lambda self, a, b: a < b
    message = 'Ensure this value is greater than or equal to %(limit_value)s.'
    code = 'min_value'


class LengthValidator(BaseValidator):
    compare = lambda self, a, b: a != b
    clean = lambda self, x: len(x)
    message = 'Ensure this value has at exactly %(limit_value)d characters (it has %(show_value)d).'
    code = 'length'


class MaxLengthValidator(LengthValidator):
    compare = lambda self, a, b: a > b
    message = 'Ensure this value has at most %(limit_value)d characters (it has %(show_value)d).'
    code = 'max_length'


class MinLengthValidator(LengthValidator):
    compare = lambda self, a, b: a < b
    message = 'Ensure this value has at least %(limit_value)d characters (it has %(show_value)d).'
    code = 'min_length'


def simple_validator(assertion=None, message='The supplied value is invalid', code='invalid'):
    """
    Create a simple validator.

    :param assertion: An Validation exception will be raised if this check returns a none True value.
    :param message: Message to raised in Validation exception if validation fails.
    :param code: Code to included in Validation exception. This can be used to customise the message at the resource
        level.

    Usage::

        >>> none_validator = simple_validator(lambda x: x is not None, message="This value cannot be none")

    This can also be used as a decorator::

        @create_validator(message="This value cannot be none")
        def none_validator(v):
            return v is not None
    """
    def inner(func):
        def wrapper(value):
            params = {'show_value': value}
            if not func(value):
                raise exceptions.ValidationError(message % params, code=code, params=params)
        return wrapper

    if assertion:
        return inner(assertion)
    else:
        return inner
