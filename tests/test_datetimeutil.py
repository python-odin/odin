# -*- coding: utf-8 -*-
import unittest
import datetime
import six
from odin import datetimeutil


class TimezonesTestCase(unittest.TestCase):
    def test_utc(self):
        self.assertEqual(datetime.timedelta(0), datetimeutil.utc.utcoffset(datetime.datetime.now()))
        self.assertEqual('UTC', datetimeutil.utc.tzname(datetime.datetime.now()))
        self.assertEqual(datetime.timedelta(0), datetimeutil.utc.dst(datetime.datetime.now()))
        self.assertEqual('UTC', str(datetimeutil.utc))
        self.assertEqual('<timezone: UTC>', repr(datetimeutil.utc))

    def test_fixed_timezone(self):
        target = datetimeutil.FixedTimezone.from_hours_minutes(10, 30)

        self.assertEqual(datetime.timedelta(hours=10, minutes=30), target.utcoffset(datetime.datetime.now()))
        self.assertEqual('10:30', target.tzname(datetime.datetime.now()))
        self.assertEqual(datetime.timedelta(0), target.dst(datetime.datetime.now()))
        self.assertEqual('10:30', str(target))
        self.assertEqual("<timezone '10:30' datetime.timedelta(0, 37800)>", repr(target))

    def test_fixed_timezone_pickling(self):
        import pickle

        target = datetimeutil.FixedTimezone.from_hours_minutes(10, 30)

        data = pickle.dumps(target)
        result = pickle.loads(data)

        self.assertEqual(result, target)


class ParseIsoDateStringTestCase(unittest.TestCase):
    def test_valid_values(self):
        self.assertEqual(
            datetime.date(2014, 1, 13),
            datetimeutil.parse_iso_date_string('2014-01-13')
        )

    def test_invalid_values(self):
        with self.assertRaises(ValueError):
            datetimeutil.parse_iso_date_string(123)
        with self.assertRaises(ValueError):
            datetimeutil.parse_iso_date_string('2014-1-13')
        with self.assertRaises(ValueError):
            datetimeutil.parse_iso_date_string('2014/01/13')


class ParseIsoTimeStringTestCase(unittest.TestCase):
    def test_valid_values(self):
        self.assertEqual(
            datetime.time(23, 53, 25, 0, datetimeutil.FixedTimezone.from_hours_minutes(10, 0)),
            datetimeutil.parse_iso_time_string('23:53:25',
                                               default_timezone=datetimeutil.FixedTimezone.from_hours_minutes(10, 0))
        )
        self.assertEqual(
            datetime.time(23, 53, 25, 0, datetimeutil.utc),
            datetimeutil.parse_iso_time_string('23:53:25')
        )
        self.assertEqual(
            datetime.time(23, 53, 25, 0, datetimeutil.utc),
            datetimeutil.parse_iso_time_string('23:53:25Z')
        )
        self.assertEqual(
            datetime.time(23, 53, 25, 432, datetimeutil.utc),
            datetimeutil.parse_iso_time_string('23:53:25.432Z')
        )
        self.assertEqual(
            datetime.time(23, 53, 25, 0, datetimeutil.FixedTimezone.from_hours_minutes(10, 0)),
            datetimeutil.parse_iso_time_string('23:53:25+10')
        )
        self.assertEqual(
            datetime.time(23, 53, 25, 432, datetimeutil.FixedTimezone.from_hours_minutes(10, 0)),
            datetimeutil.parse_iso_time_string('23:53:25.432+10')
        )
        self.assertEqual(
            datetime.time(23, 53, 25, 0, datetimeutil.FixedTimezone.from_hours_minutes(10, 30)),
            datetimeutil.parse_iso_time_string('23:53:25+10:30')
        )
        self.assertEqual(
            datetime.time(23, 53, 25, 432, datetimeutil.FixedTimezone.from_hours_minutes(-10, -30)),
            datetimeutil.parse_iso_time_string('23:53:25.432-10:30')
        )

    def test_invalid_values(self):
        with self.assertRaises(ValueError):
            datetimeutil.parse_iso_time_string(123)
        with self.assertRaises(ValueError):
            datetimeutil.parse_iso_time_string('23:53:25EST')


class ParseIsoDateTimeStringTestCase(unittest.TestCase):
    def test_valid_values(self):
        self.assertEqual(
            datetime.datetime(2014, 1, 13, 0, 28, 33, 0, datetimeutil.utc),
            datetimeutil.parse_iso_datetime_string('2014-01-13T00:28:33')
        )
        self.assertEqual(
            datetime.datetime(2014, 1, 13, 0, 28, 33, 0, datetimeutil.utc),
            datetimeutil.parse_iso_datetime_string('2014-01-13T00:28:33Z')
        )
        self.assertEqual(
            datetime.datetime(2014, 1, 13, 0, 28, 33, 432, datetimeutil.utc),
            datetimeutil.parse_iso_datetime_string('2014-01-13T00:28:33.432Z')
        )
        self.assertEqual(
            datetime.datetime(2014, 1, 13, 0, 28, 33, 0, datetimeutil.FixedTimezone.from_hours_minutes(10, 0)),
            datetimeutil.parse_iso_datetime_string('2014-01-13T00:28:33+10')
        )
        self.assertEqual(
            datetime.datetime(2014, 1, 13, 0, 28, 33, 432, datetimeutil.FixedTimezone.from_hours_minutes(10, 0)),
            datetimeutil.parse_iso_datetime_string('2014-01-13T00:28:33.432+10')
        )
        self.assertEqual(
            datetime.datetime(2014, 1, 13, 0, 28, 33, 0, datetimeutil.FixedTimezone.from_hours_minutes(10, 30)),
            datetimeutil.parse_iso_datetime_string('2014-01-13T00:28:33+10:30')
        )
        self.assertEqual(
            datetime.datetime(2014, 1, 13, 0, 28, 33, 432, datetimeutil.FixedTimezone.from_hours_minutes(-10, -30)),
            datetimeutil.parse_iso_datetime_string('2014-01-13T00:28:33.432-10:30')
        )
        self.assertEqual(
            datetime.datetime(2014, 1, 13, 0, 28, 33, 432, datetimeutil.FixedTimezone.from_hours_minutes(10, 30)),
            datetimeutil.parse_iso_datetime_string('2014-01-13T00:28:33.432+1030')
        )

        # Non-Standard but close formats that are common
        self.assertEqual(
            datetime.datetime(2014, 1, 13, 0, 28, 33, 0, datetimeutil.utc),
            datetimeutil.parse_iso_datetime_string('2014-01-13 00:28:33Z')
        )
        self.assertEqual(
            datetime.datetime(2014, 1, 13, 0, 28, 33, 0, datetimeutil.utc),
            datetimeutil.parse_iso_datetime_string('2014-01-13 00:28:33 GMT')
        )

    def test_invalid_values(self):
        self.assertRaises(ValueError, datetimeutil.parse_iso_datetime_string, 123)
        self.assertRaises(ValueError, datetimeutil.parse_iso_datetime_string, '2014-1-13T00:28:33Z')
        self.assertRaises(ValueError, datetimeutil.parse_iso_datetime_string, '2014/1/13T00:28:33Z')
        self.assertRaises(ValueError, datetimeutil.parse_iso_datetime_string, '2014-01-13T00:28:33EST')


class ToDateStringTestCase(unittest.TestCase):
    def test_naive_datetime(self):
        dt = datetime.datetime(2013, 7, 13, 16, 54, 46, 123000)
        actual = datetimeutil.to_ecma_datetime_string(dt, datetimeutil.utc)  # assume UTC to simplify this particular test
        self.assertEqual("2013-07-13T16:54:46.123Z", actual)

    def test_aware_datetime(self):
        dt = datetime.datetime(2013, 7, 13, 16, 54, 46, 123000, datetimeutil.utc)
        actual = datetimeutil.to_ecma_datetime_string(dt, datetimeutil.utc)
        self.assertEqual("2013-07-13T16:54:46.123Z", actual)


class ParseHttpDateStringTestCase(unittest.TestCase):
    def test_valid_values(self):
        self.assertEqual(
            datetime.datetime(2012, 8, 29, 17, 12, 58, tzinfo=datetimeutil.FixedTimezone.from_hours_minutes(10, 30)),
            datetimeutil.parse_http_datetime_string('Wed Aug 29 17:12:58 +1030 2012')
        )
        self.assertEqual(
            datetime.datetime(2012, 8, 29, 17, 12, 58, tzinfo=datetimeutil.FixedTimezone.from_hours_minutes(8, 00)),
            datetimeutil.parse_http_datetime_string('Wed Aug 29 17:12:58 +0800 2012')
        )
        self.assertEqual(
            datetime.datetime(2012, 8, 29, 17, 12, 58, tzinfo=datetimeutil.FixedTimezone.from_hours_minutes(-9, 0)),
            datetimeutil.parse_http_datetime_string('Wed Aug 29 17:12:58 -0900 2012')
        )
        self.assertEqual(
            datetime.datetime(2012, 8, 29, 17, 12, 58, tzinfo=datetimeutil.FixedTimezone.from_hours_minutes(-9, -30)),
            datetimeutil.parse_http_datetime_string('Wed Aug 29 17:12:58 -0930 2012')
        )
        # Alternate position for the year
        self.assertEqual(
            datetime.datetime(2012, 8, 29, 17, 12, 58, tzinfo=datetimeutil.FixedTimezone.from_hours_minutes(-9, -30)),
            datetimeutil.parse_http_datetime_string('Wed, Aug 29 2012 17:12:58 -0930')
        )

    def test_invalid_values(self):
        self.assertRaises(ValueError, datetimeutil.parse_http_datetime_string, 123)
        self.assertRaises(ValueError, datetimeutil.parse_http_datetime_string, '2014-1-13T00:28:33Z')
        self.assertRaises(ValueError, datetimeutil.parse_http_datetime_string, '2014/1/13T00:28:33Z')
        self.assertRaises(ValueError, datetimeutil.parse_http_datetime_string, '2014-01-13T00:28:33EST')


