# -*- coding: utf-8 -*-
import unittest
from odin import filtering
from odin.contrib import filter_query


class FilterQueryTestCase(unittest.TestCase):
    def test_single_operator(self):
        ftr = filter_query.parse("field == 123")


    def test_string_value(self):
        pass

    def test_int_value(self):
        pass

    def test_float_value(self):
        pass

    def test_none_value(self):
        pass

    def test_single_operator(self):
        pass

    def test_and_clause(self):
        pass

    def test_or_clause(self):
        pass
