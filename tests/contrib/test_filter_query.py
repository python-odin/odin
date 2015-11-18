# -*- coding: utf-8 -*-
import unittest
from odin import filtering
from odin.contrib import filter_query


class FilterQueryTestCase(unittest.TestCase):
    @unittest.expectedFailure
    def test_single_operator(self):
        ftr = filter_query.parse("foo == 123")

        self.assertIsInstance(flt, filtering.FilterChain)
        # self.assertEqual(1, len(flt.))

    @unittest.expectedFailure
    def test_string_value(self):
        ftr = filter_query.parse('foo == "123 bar"')

        self.assertIsInstance(flt, filtering.FilterChain)

    @unittest.expectedFailure
    def test_int_value(self):
        ftr = filter_query.parse("foo == 123")

        self.assertIsInstance(flt, filtering.FilterChain)

    @unittest.expectedFailure
    def test_float_value(self):
        ftr = filter_query.parse("foo == 123.45")

        self.assertIsInstance(flt, filtering.FilterChain)

    @unittest.expectedFailure
    def test_none_value(self):
        ftr = filter_query.parse("foo == None")

        self.assertIsInstance(flt, filtering.FilterChain)

        ftr = filter_query.parse("foo == NULL")

        self.assertIsInstance(flt, filtering.FilterChain)

    @unittest.expectedFailure
    def test_and_clause(self):
        ftr = filter_query.parse('foo == "bar" AND bar == 123')

        self.assertIsInstance(flt, filtering.FilterChain)

    @unittest.expectedFailure
    def test_or_clause(self):
        ftr = filter_query.parse('foo == "bar" OR bar == 123')

        self.assertIsInstance(flt, filtering.FilterChain)

    @unittest.expectedFailure
    def test_chained_clauses(self):
        ftr = filter_query.parse('foo == "bar" OR bar == 123 AND eek == 321')

        self.assertIsInstance(flt, filtering.FilterChain)

    @unittest.expectedFailure
    def test_nested_clauses(self):
        ftr = filter_query.parse('((foo == "bar" OR bar == 123) AND eek == 321)')

        self.assertIsInstance(flt, filtering.FilterChain)
