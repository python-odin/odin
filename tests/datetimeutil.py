# -*- coding: utf-8 -*-
import unittest
import datetime
from odin import datetimeutil


class ParseDateStringTestCase(unittest.TestCase):
    def test_valid_string(self):
        actual = datetimeutil.parse_ecma_date_string("2013-07-13T16:54:46.123Z", False)
        self.assertEqual(actual, datetime.datetime(2013, 7, 13, 16, 54, 46, 123000, datetimeutil.utc))

    def test_invalid_string_none(self):
        with self.assertRaises(ValueError):
            datetimeutil.parse_ecma_date_string(None)

    def test_invalid_string_wrong_format(self):
        with self.assertRaises(ValueError):
            datetimeutil.parse_ecma_date_string("2013/07/13T16:54:46.123")


class ToDateStringTestCase(unittest.TestCase):
    def test_naive_datetime(self):
        dt = datetime.datetime(2013, 7, 13, 16, 54, 46, 123000)
        actual = datetimeutil.to_ecma_date_string(dt, False)  # assume UTC to simplify this particular test
        self.assertEqual("2013-07-13T16:54:46.123Z", actual)

    def test_aware_datetime(self):
        dt = datetime.datetime(2013, 7, 13, 16, 54, 46, 123000, datetimeutil.utc)
        actual = datetimeutil.to_ecma_date_string(dt, False)
        self.assertEqual("2013-07-13T16:54:46.123Z", actual)
