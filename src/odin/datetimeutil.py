# -*- coding: utf-8 -*-
import datetime
import re
import time
import six

ZERO = datetime.timedelta(0)
STD_OFFSET = datetime.timedelta(seconds=-time.timezone)
DST_OFFSET = datetime.timedelta(seconds=-time.altzone) if time.daylight else STD_OFFSET
DST_DIFF = DST_OFFSET - STD_OFFSET


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
        if self._is_dst(dt):
            return DST_OFFSET
        else:
            return STD_OFFSET

    def dst(self, dt):
        if self._is_dst(dt):
            return DST_DIFF
        else:
            return ZERO

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


ECMA_ISO_DATE_STRING_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})\.(\d{3})Z$")


def parse_ecma_date_string(date_string, to_local_time=True):
    """
    Parse a date in the string format defined in ECMA-262.

    See ECMA international standard: ECMA-262 section 15.9.1.15

    ``to_local_time`` option will return the datetime in the current local timezone.
    """
    if not isinstance(date_string, six.string_types):
        raise ValueError("Expected string")

    match = ECMA_ISO_DATE_STRING_RE.match(date_string)
    if not match:
        raise ValueError("Expected ECMA 262 formatted date string.")

    dtt = (
        int(match.group(1)),  # Year
        int(match.group(2)),  # Month
        int(match.group(3)),  # Day
        int(match.group(4)),  # Hour
        int(match.group(5)),  # Minute
        int(match.group(6)),  # Second
        int(match.group(7))*1000,  # Microsecond
        utc  # Timezone
    )
    dt = datetime.datetime(*dtt)
    if to_local_time:
        return dt.astimezone(local)
    else:
        return dt


def to_ecma_date_string(dt, assume_local_time=True):
    """
    Convert a python datetime into the string format defined in ECMA-262.

    See ECMA international standard: ECMA-262 section 15.9.1.15

    ``assume_local_time`` if true will assume the date time is in local time if the object is a naive date time object;
        else assumes the time value is utc.
    """
    assert isinstance(dt, datetime.datetime)

    dt = get_tz_aware_dt(dt, local if assume_local_time else utc).astimezone(utc)
    return "%4i-%02i-%02iT%02i:%02i:%02i.%03iZ" % (
        dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond/1000)
