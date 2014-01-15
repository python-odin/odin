# -*- coding: utf-8 -*-
import datetime
from odin import datetimeutil


def date_iso_format(value):
    """
    Serialise a datetime.date to ISO string format.
    """
    assert isinstance(value, datetime.date)
    return value.isoformat()


class TimeIsoFormat(object):
    """
    Serialise a datetime.time to ISO string format.
    """
    def __init__(self, default_timezone=datetimeutil.local):
        self.default_timezone = default_timezone

    def __call__(self, value):
        assert isinstance(value, datetime.time)
        if value.tzinfo is None:
            value = value.replace(tzinfo=self.default_timezone)
        return value.isoformat()

time_iso_format = TimeIsoFormat()


class DatetimeIsoFormat(object):
    """
    Serialise a datetime.datetime to ISO string format.
    """
    def __init__(self, default_timezone=datetimeutil.local):
        self.default_timezone = default_timezone

    def __call__(self, value):
        assert isinstance(value, datetime.datetime)
        if value.tzinfo is None:
            value = value.replace(tzinfo=self.default_timezone)
        return value.isoformat()

datetime_iso_format = DatetimeIsoFormat()


class DatetimeEcmaFormat(object):
    """
    Serialize a datetime object into the ECMA defined format.
    """
    input_type = datetime.datetime

    def __init__(self, assume_local=True, default_timezone=datetimeutil.local):
        self.default_timezone = datetimeutil.local if assume_local else default_timezone

    def __call__(self, value):
        assert isinstance(value, self.input_type)
        return datetimeutil.to_ecma_datetime_string(value, self.default_timezone)

datetime_ecma_format = DatetimeEcmaFormat()
