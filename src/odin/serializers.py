import datetime
from typing import Union, Callable, Any, Dict

from odin import datetimeutil
from odin.compatibility import deprecated

StringFormatter = Callable[[Any], str]
STRING_TYPES: Dict[type, StringFormatter] = {}


def register_string_type(data_type: type, serialise_method: StringFormatter):
    """
    Register a data type serialise method that results in a string.

    :param data_type: a type instance that string data type should match.
    :param serialise_method: a method that accepts a single value that will return a string representation of
        the serialised type.

    """
    STRING_TYPES[data_type] = serialise_method


def date_iso_format(value: datetime.date) -> str:
    """
    Serialise a datetime.date to ISO string format.
    """
    return value.isoformat()


@deprecated(
    "Defaulting the timezone should be preformed by the fields only, this confuses things. "
    "Most codecs have already migrated to not use this class."
)
class DatetimeIsoFormat:
    """
    Serialise a datetime.time or datetime.datetime to ISO string format.
    """

    def __init__(self, default_timezone=datetimeutil.local):
        self.default_timezone = default_timezone

    def __call__(self, value: Union[datetime.time, datetime.datetime]) -> str:
        if value.tzinfo is None:
            value = value.replace(tzinfo=self.default_timezone)
        return value.isoformat()


TimeIsoFormat = DatetimeIsoFormat

# Mapping for compatibility
datetime_iso_format = datetime.datetime.isoformat
time_iso_format = datetime.time.isoformat
