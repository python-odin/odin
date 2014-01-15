# -*- coding: utf-8 -*-
import datetime
import re
import time
import six

ZERO = datetime.timedelta(0)
LOCAL_STD_OFFSET = datetime.timedelta(seconds=-time.timezone)
LOCAL_DST_OFFSET = datetime.timedelta(seconds=-time.altzone) if time.daylight else LOCAL_STD_OFFSET
LOCAL_DST_DIFF = LOCAL_DST_OFFSET - LOCAL_STD_OFFSET


class UTC(datetime.tzinfo):
    """
    UTC timezone.
    """
    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO

    def __str__(self):
        return "UTC"

    def __repr__(self):
        return "<timezone: %s>" % self


class LocalTimezone(datetime.tzinfo):
    """
    The current local timezone (according to the platform)
    """
    def utcoffset(self, dt):
        return LOCAL_DST_OFFSET if self._is_dst(dt) else LOCAL_STD_OFFSET

    def dst(self, dt):
        return LOCAL_DST_DIFF if self._is_dst(dt) else ZERO

    def tzname(self, dt):
        return time.tzname[self._is_dst(dt)]

    def _is_dst(self, dt):
        stamp = time.mktime((dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.weekday(), 0, 0))
        tt = time.localtime(stamp)
        return tt.tm_isdst > 0

    def __str__(self):
        return time.tzname[0]

    def __repr__(self):
        return "<timezone: %s>" % self


class FixedTimezone(datetime.tzinfo):
    """
    A fixed timezone for when a timezone is specified by a numerical offset and no dst information is available.
    """
    def __init__(self, offset_hours, offset_minutes, name):
        super(FixedTimezone, self).__init__()
        self.offset = datetime.timedelta(hours=offset_hours, minutes=offset_minutes)
        self.name = name

    def utcoffset(self, dt):
        return self.offset

    def dst(self, dt):
        return ZERO

    def tzname(self, dt):
        return self.name

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<timezone %r %r>" % (self.name, self.offset)


utc = UTC()
local = LocalTimezone()


def get_tz_aware_dt(dt, assumed_tz=local):
    """
    Get a time zone aware date time from a supplied date time.

    If dt is already timezone aware it will be returned unchanged.
    If dt is not aware it will be assumed that dt is in local time.
    """
    assert isinstance(dt, datetime.datetime)

    if dt.tzinfo:
        return dt
    else:
        return dt.replace(tzinfo=assumed_tz)


ISO8601_DATE_STRING_RE = re.compile(
    r"^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})$")
ISO8601_TIME_STRING_RE = re.compile(
    r"^(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})(\.(?P<microseconds>\d+))?"
    r"(?P<timezone>Z|((?P<tz_sign>[-+])(?P<tz_hour>\d{2})(:(?P<tz_minute>\d{2}))?))?$")
ISO8601_DATETIME_STRING_RE = re.compile(
    r"^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})T"
    r"(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})(\.(?P<microseconds>\d+))?"
    r"(?P<timezone>Z|((?P<tz_sign>[-+])(?P<tz_hour>\d{2})(:(?P<tz_minute>\d{2}))?))?$")


def parse_iso_date_string(date_string):
    """
    Parse a date in the string format defined in ISO 8601.
    """
    if not isinstance(date_string, six.string_types):
        raise ValueError("Expected string")

    matches = ISO8601_DATE_STRING_RE.match(date_string)
    if not matches:
        raise ValueError("Expected ISO 8601 formatted date string.")

    groups = matches.groupdict()
    return datetime.date(
        int(groups['year']),
        int(groups['month']),
        int(groups['day']),
    )


def _parse_timezone(groups, default_timezone=utc):
    if groups['timezone'] is None:
        return default_timezone

    if groups['timezone'] == 'Z':
        return utc

    sign = groups['tz_sign']
    hours = int(groups['tz_hour'])
    minutes = int(groups['tz_minute'] or 0)
    name = "%s%02d:%02d" % (sign, hours, minutes)

    if sign == '-':
        hours = -hours
        minutes = -minutes

    return FixedTimezone(hours, minutes, name)


def parse_iso_time_string(time_string, default_timezone=utc):
    """
    Parse a time in the string format defined in ISO 8601.
    """
    if not isinstance(time_string, six.string_types):
        raise ValueError("Expected string")

    matches = ISO8601_TIME_STRING_RE.match(time_string)
    if not matches:
        raise ValueError("Expected ISO 8601 formatted time string.")

    groups = matches.groupdict()
    tz = _parse_timezone(groups, default_timezone)
    return datetime.time(
        int(groups['hour']),
        int(groups['minute']),
        int(groups['second']),
        int(groups['microseconds'] or 0),
        tz
    )


def parse_iso_datetime_string(datetime_string, default_timezone=utc):
    """
    Parse a datetime in the string format defined in ISO 8601.
    """
    if not isinstance(datetime_string, six.string_types):
        raise ValueError("Expected string")

    matches = ISO8601_DATETIME_STRING_RE.match(datetime_string)
    if not matches:
        raise ValueError("Expected ISO 8601 formatted datetime string.")

    groups = matches.groupdict()
    tz = _parse_timezone(groups, default_timezone)
    return datetime.datetime(
        int(groups['year']),
        int(groups['month']),
        int(groups['day']),
        int(groups['hour']),
        int(groups['minute']),
        int(groups['second']),
        int(groups['microseconds'] or 0),
        tz
    )


def to_ecma_datetime_string(dt, default_timezone=local):
    """
    Convert a python datetime into the string format defined in ECMA-262.

    See ECMA international standard: ECMA-262 section 15.9.1.15

    ``assume_local_time`` if true will assume the date time is in local time if the object is a naive date time object;
        else assumes the time value is utc.
    """
    assert isinstance(dt, datetime.datetime)

    dt = get_tz_aware_dt(dt, default_timezone).astimezone(utc)
    return "%4i-%02i-%02iT%02i:%02i:%02i.%03iZ" % (
        dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond/1000)
