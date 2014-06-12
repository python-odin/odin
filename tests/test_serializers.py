# -*- coding: utf-8 -*-
import unittest
import datetime
from odin import datetimeutil
from odin import serializers


class SerializerTestCase(unittest.TestCase):
    def test_date_iso_format(self):
        self.assertEqual("2014-01-16", serializers.date_iso_format(datetime.date(2014, 1, 16)))

    def test_time_iso_format(self):
        self.assertEqual(
            "00:29:32+00:00",
            serializers.TimeIsoFormat(datetimeutil.utc)(
                datetime.time(0, 29, 32)))
        self.assertEqual(
            "00:29:32+10:00",
            serializers.TimeIsoFormat(datetimeutil.utc)(
                datetime.time(0, 29, 32, tzinfo=datetimeutil.FixedTimezone.from_hours_minutes(10, 0))))

        self.assertEqual(
            "00:29:32-03:30",
            serializers.TimeIsoFormat(datetimeutil.FixedTimezone.from_hours_minutes(-3, -30))(
                datetime.time(0, 29, 32)))
        self.assertEqual(
            "00:29:32+10:00",
            serializers.TimeIsoFormat(datetimeutil.FixedTimezone.from_hours_minutes(-3, -30))(
                datetime.time(0, 29, 32, tzinfo=datetimeutil.FixedTimezone.from_hours_minutes(10, 0))))

    def test_datetime_iso_format(self):
        self.assertEqual(
            "2014-01-16T00:29:32+00:00",
            serializers.DatetimeIsoFormat(datetimeutil.utc)(
                datetime.datetime(2014, 1, 16, 0, 29, 32)))
        self.assertEqual(
            "2014-01-16T00:29:32+10:00",
            serializers.DatetimeIsoFormat(datetimeutil.utc)(
                datetime.datetime(2014, 1, 16, 0, 29, 32, tzinfo=datetimeutil.FixedTimezone.from_hours_minutes(10, 0))))

        self.assertEqual(
            "2014-01-16T00:29:32-03:30",
            serializers.DatetimeIsoFormat(datetimeutil.FixedTimezone.from_hours_minutes(-3, -30))(
                datetime.datetime(2014, 1, 16, 0, 29, 32)))
        self.assertEqual(
            "2014-01-16T00:29:32+10:00",
            serializers.DatetimeIsoFormat(datetimeutil.FixedTimezone.from_hours_minutes(-3, -30))(
                datetime.datetime(2014, 1, 16, 0, 29, 32, tzinfo=datetimeutil.FixedTimezone.from_hours_minutes(10, 0))))

    def test_datetime_ecma_format(self):
        self.assertEqual(
            "2014-01-16T00:29:32.000Z",
            serializers.DatetimeEcmaFormat(False, default_timezone=datetimeutil.utc)(
                datetime.datetime(2014, 1, 16, 0, 29, 32)))
        self.assertEqual(
            "2014-01-15T14:29:32.000Z",
            serializers.DatetimeEcmaFormat(False, default_timezone=datetimeutil.utc)(
                datetime.datetime(2014, 1, 16, 0, 29, 32, tzinfo=datetimeutil.FixedTimezone.from_hours_minutes(10, 0))))

        self.assertEqual(
            "2014-01-16T03:59:32.000Z",
            serializers.DatetimeEcmaFormat(False,
                                           default_timezone=datetimeutil.FixedTimezone.from_hours_minutes(-3, -30))(
                datetime.datetime(2014, 1, 16, 0, 29, 32)))
        self.assertEqual(
            "2014-01-15T14:29:32.000Z",
            serializers.DatetimeEcmaFormat(False,
                                           default_timezone=datetimeutil.FixedTimezone.from_hours_minutes(-3, -30))(
                datetime.datetime(2014, 1, 16, 0, 29, 32, tzinfo=datetimeutil.FixedTimezone.from_hours_minutes(10, 0))))

