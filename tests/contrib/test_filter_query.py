# -*- coding: utf-8 -*-
import pytest
from odin import filtering
from odin.contrib import filter_query


class TestFilterQuery(object):
    def test_single_operator(self):
        pytest.skip("Proof of concept code")

        ftr = filter_query.parse("foo == 123")

        assert isinstance(ftr, filtering.FilterChain)
        # self.assertEqual(1, len(ftr.))

    def test_string_value(self):
        pytest.skip("Proof of concept code")

        ftr = filter_query.parse('foo == "123 bar"')

        assert isinstance(ftr, filtering.FilterChain)

    def test_int_value(self):
        pytest.skip("Proof of concept code")

        ftr = filter_query.parse("foo == 123")

        assert isinstance(ftr, filtering.FilterChain)

    def test_float_value(self):
        pytest.skip("Proof of concept code")

        ftr = filter_query.parse("foo == 123.45")

        assert isinstance(ftr, filtering.FilterChain)

    def test_none_value(self):
        pytest.skip("Proof of concept code")

        ftr = filter_query.parse("foo == None")

        assert isinstance(ftr, filtering.FilterChain)

        ftr = filter_query.parse("foo == NULL")

        assert isinstance(ftr, filtering.FilterChain)

    def test_and_clause(self):
        pytest.skip("Proof of concept code")

        ftr = filter_query.parse('foo == "bar" AND bar == 123')

        assert isinstance(ftr, filtering.FilterChain)

    def test_or_clause(self):
        pytest.skip("Proof of concept code")

        ftr = filter_query.parse('foo == "bar" OR bar == 123')

        assert isinstance(ftr, filtering.FilterChain)

    def test_chained_clauses(self):
        pytest.skip("Proof of concept code")

        ftr = filter_query.parse('foo == "bar" OR bar == 123 AND eek == 321')

        assert isinstance(ftr, filtering.FilterChain)

    def test_nested_clauses(self):
        pytest.skip("Proof of concept code")

        ftr = filter_query.parse('((foo == "bar" OR bar == 123) AND eek == 321)')

        assert isinstance(ftr, filtering.FilterChain)
