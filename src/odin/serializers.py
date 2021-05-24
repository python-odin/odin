# -*- coding: utf-8 -*-
from __future__ import absolute_import, division

import datetime
from typing import Union

from odin import datetimeutil
from odin.compatibility import deprecated

STRING_TYPES = {}


def register_string_type(data_type, serialise_method):
    """
    Register a data type serialise method that results in a string.

    :param data_type: a type instance that string data type should match.
    :param serialise_method: a method that accepts a single value that will return a string representation of
        the serialised type.

    """
    STRING_TYPES[data_type] = serialise_method


def date_iso_format(value):
    # type: (datetime.date) -> str
    """
    Serialise a datetime.date to ISO string format.
    """
    return value.isoformat()


@deprecated(
    "Defaulting the timezone should be preformed by the fields only, this confuses things. "
    "Most codecs have already migrated to not use this class."
)
class DatetimeIsoFormat(object):
    """
    Serialise a datetime.time or datetime.datetime to ISO string format.
    """

    def __init__(self, default_timezone=datetimeutil.local):
        self.default_timezone = default_timezone

    def __call__(self, value):
        # type: (Union[datetime.time, datetime.datetime]) -> str
        if value.tzinfo is None:
            value = value.replace(tzinfo=self.default_timezone)
        return value.isoformat()


TimeIsoFormat = DatetimeIsoFormat


def datetime_iso_format(value):
    # type: (datetime.datetime) -> str
    """
    Serialise a datetime.datetime to ISO string format.
    """
    return value.isoformat()


def time_iso_format(value):
    # type: (datetime.time) -> str
    """
    Serialise a datetime.time to ISO string format.
    """
    return value.isoformat()


@deprecated(
    "Defaulting the timezone should be preformed by the fields only, this confuses things. "
    "Most codecs have already migrated to not use this class."
)
class DatetimeEcmaFormat(object):
    """
    Serialize a datetime object into the ECMA defined format.
    """

    input_type = datetime.datetime

    def __init__(self, assume_local=True, default_timezone=datetimeutil.local):
        self.default_timezone = datetimeutil.local if assume_local else default_timezone

    def __call__(self, value):
        return datetimeutil.to_ecma_datetime_string(value, self.default_timezone)


datetime_ecma_format = DatetimeEcmaFormat()
