import datetime
import re
import time
from email.utils import parsedate_tz as parse_http_datetime
from email.utils import formatdate as format_http_datetime  # noqa
from typing import Union, Type


class IgnoreTimezone:
    pass


IgnorableTimezone = Union[datetime.tzinfo, Type[IgnoreTimezone]]


ZERO = datetime.timedelta(0)
LOCAL_STD_OFFSET = datetime.timedelta(seconds=-time.timezone)
LOCAL_DST_OFFSET = (
    datetime.timedelta(seconds=-time.altzone) if time.daylight else LOCAL_STD_OFFSET
)
LOCAL_DST_DIFF = LOCAL_DST_OFFSET - LOCAL_STD_OFFSET


# Keep for backwards compatibility
utc = datetime.timezone.utc


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

    @staticmethod
    def _is_dst(dt):
        stamp = time.mktime(
            (
                dt.year,
                dt.month,
                dt.day,
                dt.hour,
                dt.minute,
                dt.second,
                dt.weekday(),
                0,
                0,
            )
        )
        tt = time.localtime(stamp)
        return tt.tm_isdst > 0

    def __str__(self):
        return time.tzname[0]

    def __repr__(self):
        return f"<timezone: {self}>"


local = LocalTimezone()


class FixedTimezone(datetime.tzinfo):
    """
    A fixed timezone for when a timezone is specified by a numerical offset and no dst information is available.
    """

    __slots__ = (
        "offset",
        "name",
    )

    @classmethod
    def from_seconds(cls, seconds: int) -> datetime.tzinfo:
        sign = "-" if seconds < 0 else ""
        minutes = abs(seconds // 60)
        hours = minutes // 60
        minutes %= 60
        name = f"{sign}{hours:02d}:{minutes:02d}"

        if sign == "-":
            hours *= -1
            minutes *= -1

        return cls(datetime.timedelta(hours=hours, minutes=minutes), name)

    @classmethod
    def from_hours_minutes(cls, hours: int, minutes: int = 0) -> datetime.tzinfo:
        sign = "-" if hours < 0 else ""
        hours = abs(hours)
        minutes = abs(minutes)
        name = f"{sign}{hours:02d}:{minutes:02d}"

        if sign == "-":
            hours *= -1
            minutes *= -1

        return cls(datetime.timedelta(hours=hours, minutes=minutes), name)

    @classmethod
    def from_groups(
        cls, groups, default_timezone: datetime.tzinfo = utc
    ) -> datetime.tzinfo:
        tz = groups["timezone"]
        if tz is None:
            return default_timezone

        if tz in ("Z", "GMT", "UTC"):
            return utc

        sign = groups["tz_sign"]
        hours = int(groups["tz_hour"])
        minutes = int(groups["tz_minute"] or 0)
        name = f"{sign}{hours:02d}:{minutes:02d}"

        if sign == "-":
            hours = -hours
            minutes = -minutes

        return cls(datetime.timedelta(hours=hours, minutes=minutes), name)

    def __init__(self, offset: datetime.timedelta = None, name: str = None):
        super().__init__()
        self.offset = offset or ZERO
        self.name = name or ""

    def utcoffset(self, _) -> datetime.timedelta:
        return self.offset

    def dst(self, _) -> datetime.timedelta:
        return ZERO

    def tzname(self, _) -> str:
        return self.name

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<timezone {self.name!r} {self.offset!r}>"

    def __eq__(self, other):
        if isinstance(other, FixedTimezone):
            return self.offset == other.offset
        return NotImplemented

    # Pickle support

    def __getstate__(self):
        return {
            "offset": self.offset,
            "name": self.name,
        }

    def __setstate__(self, state):
        self.offset = state.get("offset")
        self.name = state.get("name")


def get_tz_aware_dt(
    dt: datetime.datetime, assumed_tz: datetime.tzinfo = local
) -> datetime.datetime:
    """
    Get a time zone aware date time from a supplied date time.

    If dt is already timezone aware it will be returned unchanged.
    If dt is not aware it will be assumed that dt is in local time.
    """
    if dt.tzinfo:
        return dt
    else:
        return dt.replace(tzinfo=assumed_tz)


def now_utc() -> datetime.datetime:
    """
    Get now in UTC (with timezone set correctly).
    """
    return datetime.datetime.now(tz=utc)


def now_local() -> datetime.datetime:
    """
    Get now in the current local timezone.
    """
    return datetime.datetime.now(tz=local)


total_seconds = datetime.timedelta.total_seconds


UNIX_EPOCH = datetime.datetime(1970, 1, 1, tzinfo=utc)
to_timestamp = datetime.datetime.timestamp

ISO8601_TIME_STRING_RE = re.compile(
    r"^(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})(\.(?P<microseconds>\d+))?"
    r"(?P<timezone>Z|((?P<tz_sign>[-+])(?P<tz_hour>\d{2})(:(?P<tz_minute>\d{2}))?))?$"
)
ISO8601_DATETIME_STRING_RE = re.compile(
    r"^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})[tT\s]"
    r"(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})(\.(?P<microseconds>\d+))? ?"
    r"(?P<timezone>Z|GMT|UTC|((?P<tz_sign>[-+])(?P<tz_hour>\d{2})(:?(?P<tz_minute>\d{2}))?))?$"
)


def parse_iso_date_string(date_string: str) -> datetime.date:
    """
    Parse a date in the string format defined in ISO 8601.
    """
    if not isinstance(date_string, str):
        raise ValueError("Expected string")

    try:
        return datetime.datetime.strptime(date_string, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Expected ISO 8601 formatted date string.")


def parse_iso_time_string(
    time_string: str, default_timezone: IgnorableTimezone = utc
) -> datetime.time:
    """
    Parse a time in the string format defined by ISO 8601.
    """
    if not isinstance(time_string, str):
        raise ValueError("Expected string")

    matches = ISO8601_TIME_STRING_RE.match(time_string)
    if not matches:
        raise ValueError("Expected ISO 8601 formatted time string.")

    groups = matches.groupdict()
    if default_timezone is IgnoreTimezone:
        tz = None
    else:
        tz = FixedTimezone.from_groups(groups, default_timezone)
    return datetime.time(
        int(groups["hour"]),
        int(groups["minute"]),
        int(groups["second"]),
        int(groups["microseconds"] or 0),
        tz,
    )


def parse_iso_datetime_string(
    datetime_string: str, default_timezone: IgnorableTimezone = utc
) -> datetime.datetime:
    """
    Parse a datetime in the string format defined by ISO 8601.
    """
    if not isinstance(datetime_string, str):
        raise ValueError("Expected string")

    matches = ISO8601_DATETIME_STRING_RE.match(datetime_string)
    if not matches:
        raise ValueError("Expected ISO 8601 formatted datetime string.")

    groups = matches.groupdict()
    if default_timezone is IgnoreTimezone:
        tz = None
    else:
        tz = FixedTimezone.from_groups(groups, default_timezone)
    return datetime.datetime(
        int(groups["year"]),
        int(groups["month"]),
        int(groups["day"]),
        int(groups["hour"]),
        int(groups["minute"]),
        int(groups["second"]),
        int(groups["microseconds"] or 0),
        tz,
    )


def to_ecma_datetime_string(
    dt: datetime.datetime, default_timezone: datetime.tzinfo = local
) -> str:
    """
    Convert a python datetime into the string format defined by ECMA-262.

    See ECMA international standard: ECMA-262 section 15.9.1.15

    ``assume_local_time`` if true will assume the date time is in local time if the object is a naive date time object;
        else assumes the time value is utc.
    """
    dt = get_tz_aware_dt(dt, default_timezone).astimezone(utc)
    return (
        f"{dt.year:4d}-{dt.month:02d}-{dt.day:02d}T"
        f"{dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}.{dt.microsecond // 1000:03d}Z"
    )


def parse_http_datetime_string(datetime_string: str) -> datetime.datetime:
    """
    Parse a datetime in the string format defined by ISO-1123 (or HTTP date time).
    """
    elements = None
    if isinstance(datetime_string, str):
        elements = parse_http_datetime(datetime_string)

    if not elements:
        raise ValueError("Expected ISO-1123 formatted datetime string.")

    return datetime.datetime(
        *elements[:6], tzinfo=FixedTimezone.from_seconds(elements[-1])
    )


HTTP_DAY_OF_WEEK = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
HTTP_MONTH = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]


def to_http_datetime_string(
    dt: datetime.datetime, default_timezone: datetime.tzinfo = local
) -> str:
    """
    Convert a python datetime into the string format defined by ISO-1123 (or HTTP date time).
    """
    dt = get_tz_aware_dt(dt, default_timezone).astimezone(utc)
    timeval = time.mktime(dt.timetuple())
    now = time.localtime(timeval)
    return (
        f"{HTTP_DAY_OF_WEEK[now[6]]}, {now[2]:02d} {HTTP_MONTH[now[1] - 1]} {now[0]:04d} "
        f"{now[3]:02d}:{now[4]:02d}:{now[5]:02d} {'GMT'}"
    )
