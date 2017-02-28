# -*- coding: utf-8 -*-
import pytest
import datetime
from odin import datetimeutil


class TestTimezones(object):
    def test_utc(self):
        assert datetime.timedelta(0) == datetimeutil.utc.utcoffset(datetime.datetime.now())
        assert 'UTC' == datetimeutil.utc.tzname(datetime.datetime.now())
        assert datetime.timedelta(0) == datetimeutil.utc.dst(datetime.datetime.now())
        assert 'UTC' == str(datetimeutil.utc)
        assert '<timezone: UTC>' == repr(datetimeutil.utc)

    def test_fixed_timezone(self):
        target = datetimeutil.FixedTimezone.from_hours_minutes(10, 30)

        assert datetime.timedelta(hours=10, minutes=30) == target.utcoffset(datetime.datetime.now())
        assert '10:30' == target.tzname(datetime.datetime.now())
        assert datetime.timedelta(0) == target.dst(datetime.datetime.now())
        assert '10:30' == str(target)
        assert "<timezone '10:30' datetime.timedelta(0, 37800)>" == repr(target)

    def test_fixed_timezone_pickling(self):
        import pickle

        target = datetimeutil.FixedTimezone.from_hours_minutes(10, 30)

        data = pickle.dumps(target)
        result = pickle.loads(data)

        assert result == target


class TestParseIsoDateString(object):
    @pytest.mark.parametrize('value', (
        '2014-01-13', '2014-1-13'
    ))
    def test_valid_values(self, value):
        assert datetime.date(2014, 1, 13) == datetimeutil.parse_iso_date_string(value)

    @pytest.mark.parametrize('value', (
        123, '2014/01/13'
    ))
    def test_invalid_values(self, value):
        pytest.raises(ValueError, datetimeutil.parse_iso_date_string, value)


class TestParseIsoTimeString(object):
    @pytest.mark.parametrize(('value', 'expected'), (
        ('23:53:25', datetime.time(23, 53, 25, 0, datetimeutil.utc)),
        ('23:53:25Z', datetime.time(23, 53, 25, 0, datetimeutil.utc)),
        ('23:53:25.432Z', datetime.time(23, 53, 25, 432, datetimeutil.utc)),
        ('23:53:25+10', datetime.time(23, 53, 25, 0, datetimeutil.FixedTimezone.from_hours_minutes(10, 0))),
        ('23:53:25.432+10', datetime.time(23, 53, 25, 432, datetimeutil.FixedTimezone.from_hours_minutes(10, 0))),
        ('23:53:25+10:30', datetime.time(23, 53, 25, 0, datetimeutil.FixedTimezone.from_hours_minutes(10, 30))),
        ('23:53:25.432-10:30', datetime.time(23, 53, 25, 432,
                                             datetimeutil.FixedTimezone.from_hours_minutes(-10, -30))),
    ))
    def test_valid_values(self, value, expected):
        assert datetimeutil.parse_iso_time_string(value) == expected

    @pytest.mark.parametrize(('value', 'default_tz', 'expected'), (
        ('23:53:25', None, datetime.time(23, 53, 25)),
        ('23:53:25', datetimeutil.IgnoreTimezone, datetime.time(23, 53, 25)),
        ('23:53:25Z', None, datetime.time(23, 53, 25, 0, datetimeutil.utc)),
        ('23:53:25Z', datetimeutil.IgnoreTimezone, datetime.time(23, 53, 25, 0)),
    ))
    def test_valid_values_timezone_handling(self, value, default_tz, expected):
        assert datetimeutil.parse_iso_time_string(value, default_tz) == expected

    def test_value_values_with_alternate_timezone(self):
        assert(
            datetime.time(23, 53, 25, 0, datetimeutil.FixedTimezone.from_hours_minutes(10, 0)) ==
            datetimeutil.parse_iso_time_string(
                '23:53:25', default_timezone=datetimeutil.FixedTimezone.from_hours_minutes(10, 0))
        )

    @pytest.mark.parametrize('value', (
        123, '23:53:25EST'
    ))
    def test_invalid_values(self, value):
        pytest.raises(ValueError, datetimeutil.parse_iso_time_string, value)


class TestParseIsoDateTimeString(object):
    @pytest.mark.parametrize(('value', 'expected'), (
        ('2014-01-13T00:28:33', datetime.datetime(2014, 1, 13, 0, 28, 33, 0, datetimeutil.utc)),
        ('2014-01-13T00:28:33Z', datetime.datetime(2014, 1, 13, 0, 28, 33, 0, datetimeutil.utc)),
        ('2014-01-13T00:28:33.432Z', datetime.datetime(2014, 1, 13, 0, 28, 33, 432, datetimeutil.utc)),
        ('2014-01-13T00:28:33+10', datetime.datetime(2014, 1, 13, 0, 28, 33, 0,
                                                     datetimeutil.FixedTimezone.from_hours_minutes(10, 0))),
        ('2014-01-13T00:28:33.432+10', datetime.datetime(2014, 1, 13, 0, 28, 33, 432,
                                                         datetimeutil.FixedTimezone.from_hours_minutes(10, 0))),
        ('2014-01-13T00:28:33+10:30', datetime.datetime(2014, 1, 13, 0, 28, 33, 0,
                                                        datetimeutil.FixedTimezone.from_hours_minutes(10, 30))),
        ('2014-01-13T00:28:33.432-10:30', datetime.datetime(2014, 1, 13, 0, 28, 33, 432,
                                                            datetimeutil.FixedTimezone.from_hours_minutes(-10, -30))),
        ('2014-01-13T00:28:33.432+1030', datetime.datetime(2014, 1, 13, 0, 28, 33, 432,
                                                           datetimeutil.FixedTimezone.from_hours_minutes(10, 30))),
        # Non-Standard but close formats that are common
        ('2014-01-13 00:28:33Z', datetime.datetime(2014, 1, 13, 0, 28, 33, 0, datetimeutil.utc)),
        ('2014-01-13 00:28:33 GMT', datetime.datetime(2014, 1, 13, 0, 28, 33, 0, datetimeutil.utc))
    ))
    def test_valid_values(self, value, expected):
        assert datetimeutil.parse_iso_datetime_string(value) == expected

    @pytest.mark.parametrize(('value', 'default_tz', 'expected'), (
        ('2014-01-13T00:28:33', None, datetime.datetime(2014, 1, 13, 0, 28, 33)),
        ('2014-01-13T00:28:33', datetimeutil.IgnoreTimezone, datetime.datetime(2014, 1, 13, 0, 28, 33)),
        ('2014-01-13T00:28:33Z', None, datetime.datetime(2014, 1, 13, 0, 28, 33, 0, datetimeutil.utc)),
        ('2014-01-13T00:28:33Z', datetimeutil.IgnoreTimezone, datetime.datetime(2014, 1, 13, 0, 28, 33)),
    ))
    def test_valid_values_timezone_handling(self, value, default_tz, expected):
        assert datetimeutil.parse_iso_datetime_string(value, default_tz) == expected

    @pytest.mark.parametrize('value', (
        123,
        '2014-1-13T00:28:33Z',
        '2014/1/13T00:28:33Z',
        '2014-01-13T00:28:33EST',
    ))
    def test_invalid_values(self, value):
        pytest.raises(ValueError, datetimeutil.parse_iso_datetime_string, value)


class TestToDateString(object):
    def test_naive_datetime(self):
        dt = datetime.datetime(2013, 7, 13, 16, 54, 46, 123000)
        actual = datetimeutil.to_ecma_datetime_string(dt, datetimeutil.utc)  # assume UTC to simplify this particular test
        assert "2013-07-13T16:54:46.123Z" == actual

    def test_aware_datetime(self):
        dt = datetime.datetime(2013, 7, 13, 16, 54, 46, 123000, datetimeutil.utc)
        actual = datetimeutil.to_ecma_datetime_string(dt, datetimeutil.utc)
        assert "2013-07-13T16:54:46.123Z" == actual


class TestParseHttpDateString(object):
    @pytest.mark.parametrize(('value', 'expected'), (
        ('Wed Aug 29 17:12:58 +1030 2012', datetime.datetime(2012, 8, 29, 17, 12, 58, 0,
                                                             datetimeutil.FixedTimezone.from_hours_minutes(10, 30))),
        ('Wed Aug 29 17:12:58 -0900 2012', datetime.datetime(2012, 8, 29, 17, 12, 58, 0,
                                                             datetimeutil.FixedTimezone.from_hours_minutes(-9, 0))),
        ('Wed Aug 29 17:12:58 -0930 2012', datetime.datetime(2012, 8, 29, 17, 12, 58, 0,
                                                             datetimeutil.FixedTimezone.from_hours_minutes(-9, -30))),
        ('Wed Aug 29 17:12:58 +0800 2012', datetime.datetime(2012, 8, 29, 17, 12, 58, 0,
                                                             datetimeutil.FixedTimezone.from_hours_minutes(8, 00))),
        # Alternate position for the year
        ('Wed, Aug 29 2012 17:12:58 -0930', datetime.datetime(2012, 8, 29, 17, 12, 58, 0,
                                                              datetimeutil.FixedTimezone.from_hours_minutes(-9, -30))),
    ))
    def test_valid_values(self, value, expected):
        assert datetimeutil.parse_http_datetime_string(value) == expected

    @pytest.mark.parametrize('value', (
        123,
        '2014-1-13T00:28:33Z',
        '2014/1/13T00:28:33Z',
        '2014-01-13T00:28:33EST',
    ))
    def test_invalid_values(self, value):
        pytest.raises(ValueError, datetimeutil.parse_http_datetime_string, value)


class TestToHttpDateString(object):
    @pytest.mark.parametrize(('value', 'expected'), (
        (datetime.datetime(2012, 8, 29, 17, 12, 58, 0, datetimeutil.FixedTimezone.from_hours_minutes(10, 30)),
         'Wed, 29 Aug 2012 06:42:58 GMT'),
        (datetime.datetime(2012, 8, 29, 17, 12, 58, 0, datetimeutil.utc),
         'Wed, 29 Aug 2012 17:12:58 GMT'),
    ))
    def test_valid_values(self, value, expected):
        assert datetimeutil.to_http_datetime_string(value) == expected
