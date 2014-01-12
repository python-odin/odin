# -*- coding: utf-8 -*-
import datetime
from odin import datetimeutil


class DatetimeEcmaFormat(object):
    """
    Serialize a datetime object into the ECMA defined format.
    """
    input_type = datetime.datetime

    def __init__(self, assume_local=True):
        self.assume_local = assume_local

    def __call__(self, value):
        assert isinstance(value, self.input_type)
        return datetimeutil.to_ecma_datetime_string(value, self.assume_local)

datetime_ecma_format = DatetimeEcmaFormat()
