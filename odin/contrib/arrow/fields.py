# -*- coding: utf-8 -*-
import arrow
import datetime

from odin import exceptions, datetimeutil
from odin.fields import Field
from odin.validators import EMPTY_VALUES

__all__ = ('ArrowField',)


class ArrowField(Field):
    """
    Field that handles datetime values encoded as a string utilising the Arrow
    date time interface.

    The format of the string is that defined by ISO-8601.

    Use the ``assume_local`` flag to customise how naive (datetime values
    with no timezone) are handled and also how dates are decoded. If
    ``assume_local`` is True naive dates are assumed to represent the current
    system timezone.

    """
    default_error_messages = {
        'invalid': "Not a valid datetime string.",
    }
    data_type_name = "ISO-8601 DateTime"

    def __init__(self, assume_local=False, **options):
        super(ArrowField, self).__init__(**options)
        self.assume_local = assume_local

    def to_python(self, value):
        if value in EMPTY_VALUES:
            return

        if isinstance(value, arrow.Arrow):
            return value

        default_timezone = datetimeutil.local if self.assume_local else datetimeutil.utc
        
        if isinstance(value, datetime.datetime):
            if value.tzinfo:
                return arrow.Arrow.fromdatetime(value)
            else:
                return arrow.Arrow.fromdatetime(value, default_timezone)
        
        try:
            return arrow.Arrow.fromdatetime(datetimeutil.parse_iso_datetime_string(value, default_timezone))
        except ValueError:
            pass

        try:
            return arrow.Arrow.fromdate(datetimeutil.parse_iso_date_string(value))
        except ValueError:
            pass
        msg = self.error_messages['invalid']
        raise exceptions.ValidationError(msg)
