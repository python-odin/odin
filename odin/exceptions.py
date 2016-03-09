# -*- coding: utf-8 -*-
from odin import registration

NON_FIELD_ERRORS = '__all__'


class ValidationError(Exception):
    """An error while validating data."""
    def __init__(self, message, code=None, params=None):
        """
        ValidationError can be passed any object that can be printed (usually
        a string), a list of objects or a dictionary.
        """
        if isinstance(message, dict):
            self.message_dict = message

        if isinstance(message, list):
            self.messages = message
        else:
            self.messages = [message]
            self.code = code
            self.params = params

    def __str__(self):
        # This is needed because, without a __str__(), printing an exception
        # instance would result in this:
        # AttributeError: ValidationError instance has no attribute 'args'
        # See http://www.python.org/doc/current/tut/node10.html#handling
        if hasattr(self, 'message_dict'):
            message_dict = self.message_dict
            return "{%s}" % ', '.join("'%s': %r" % (key, message_dict[key]) for key in sorted(message_dict))
        return repr(self.messages)

    def __repr__(self):
        return 'ValidationError(%s)' % self

    @property
    def error_messages(self):
        if hasattr(self, 'message_dict'):
            return self.message_dict
        else:
            return self.messages

    def update_error_dict(self, error_dict):
        if hasattr(self, 'message_dict'):
            if error_dict:
                for k, v in self.message_dict.items():
                    error_dict.setdefault(k, []).extend(v)
            else:
                error_dict = self.message_dict
        else:
            error_dict[NON_FIELD_ERRORS] = self.messages
        return error_dict


def validation_error_handler(exception, field, errors):
    if hasattr(exception, 'code') and exception.code in field.error_messages:
        message = field.error_messages[exception.code]
        if exception.params:
            message = message % exception.params
        errors.append(message)
    else:
        errors.extend(exception.messages)
registration.register_validation_error_handler(ValidationError, validation_error_handler)


class ResourceException(ValidationError):
    """
    Errors raised when generating resource from files.

    Exception inherits from ValidationError for backwards compatibility.

    """


class MappingError(Exception):
    """
    Exceptions related to mapping, will typically be a more specific `MappingSetupError` or `MappingExecutionError`.
    """


class MappingSetupError(MappingError):
    """
    Exception raised during the setup of mapping rules.
    """


class MappingExecutionError(MappingError):
    """
    Exception raised during the execution of mapping rules.
    """


class CodecError(Exception):
    """
    Exception raised by a codec during an operation.
    """


class CodecDecodeError(CodecError):
    """
    Exception raised by a codec during a decoding operation.
    """


class CodecEncodeError(CodecError):
    """
    Exception raised by a codec during an encoding operation.
    """


class TraversalError(Exception):
    """
    Exception raised during a traversal operation.
    """
    def __init__(self, path, *args, **kwargs):
        super(TraversalError, self).__init__(*args, **kwargs)
        self.path = path


class InvalidPathError(TraversalError):
    """
    Raised when a path is invalid (eg referencing an unknown field)
    """


class NoMatchError(TraversalError):
    """
    When traversing a path to get a value no match was found.
    """


class MultipleMatchesError(TraversalError):
    """
    When traversing a path to get a single value, a filtering operation matched multiple values.
    """
