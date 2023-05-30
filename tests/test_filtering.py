import os

import pytest

from odin import filtering
from odin.codecs import json_codec
from odin.traversal import TraversalPath

# Open library fixture
with open(os.path.join(os.path.dirname(__file__), "fixtures", "library.json")) as f:
    library = json_codec.load(f)

first_book = TraversalPath.parse("books[0]").get_value(library)


class TestFilter:
    def test_matches_top_level_resource(self):
        flt = filtering.Equal("title", "Consider Phlebas")
        assert flt(first_book)

    def test_matches_multiple_matches_resource(self):
        # Less than fiction $20 with a single author and not fantasy
        flt = filtering.And(
            filtering.Equal("fiction", True),
            filtering.LessThan("rrp", 20),
            filtering.Equal("authors", 1, len),
            filtering.NotEqual("genre", "fantasy"),
        )
        assert flt(first_book)

    def test_matches_sub_resource(self):
        flt = filtering.Equal("publisher.name", "Macmillan")
        assert flt(first_book)

    def test_find_sub_resources(self):
        flt = filtering.Equal("fiction", True)
        # Some fiction?
        assert flt.any(library.books)
        # All fiction
        assert not flt.all(library.books)

    def test_resource_field_does_not_exist(self):
        flt = filtering.Equal("title", "Public Library")
        assert not flt(library)


class TestFilterChain:
    def test_empty_description(self):
        flt = filtering.And()
        assert "" == str(flt)

    def test_description(self):
        flt = filtering.And(
            filtering.Equal("fiction", True),
            filtering.LessThan("rrp", 20),
        )
        assert "(fiction == True AND rrp < 20)" == str(flt)

    def test_combining_same_type(self):
        flt1 = filtering.And(
            filtering.Equal("fiction", True),
            filtering.LessThan("rrp", 20),
        )
        flt2 = filtering.And(
            filtering.Equal("authors", 1, len),
            filtering.NotEqual("genre", "fantasy"),
        )
        flt = flt1 + flt2

        assert (
            "(fiction == True AND rrp < 20 AND len(authors) == 1 AND genre != 'fantasy')"
            == str(flt)
        )
        assert len(flt) == 4

    def test_combine_with_comparison(self):
        flt1 = filtering.And(
            filtering.Equal("fiction", True),
            filtering.LessThan("rrp", 20),
        )
        flt = flt1 + filtering.Equal("authors", 1, len)

        assert "(fiction == True AND rrp < 20 AND len(authors) == 1)" == str(flt)

    def test_combine_with_other_type(self):
        flt1 = filtering.And(
            filtering.Equal("fiction", True),
            filtering.LessThan("rrp", 20),
        )
        pytest.raises(TypeError, lambda: flt1 + "abc")


class FilterComparisonTest(filtering.FilterComparison):
    operator_symbols = ["%"]


class TestFilterComparison:
    def test_description(self):
        comp = FilterComparisonTest("foo", "bar")
        assert "foo % 'bar'" == str(comp)

        comp = FilterComparisonTest("foo", 42)
        assert "foo % 42" == str(comp)

        comp = FilterComparisonTest("foo", "bar", any)
        assert "any(foo) % 'bar'" == str(comp)

    def test_equal(self):
        comp = filtering.Equal("foo", "bar")
        assert "foo == 'bar'" == str(comp)
        assert comp.compare_operator("bar", "bar")

    def test_not_equal(self):
        comp = filtering.NotEqual("foo", "bar")
        assert "foo != 'bar'" == str(comp)
        assert comp.compare_operator("bar", "eek")

    def test_less_than(self):
        comp = filtering.LessThan("foo", 5)
        assert "foo < 5" == str(comp)
        assert comp.compare_operator(4, 5)
        assert not comp.compare_operator(5, 5)
        assert not comp.compare_operator(6, 5)

    def test_less_than_or_equal(self):
        comp = filtering.LessThanOrEqual("foo", 5)
        assert "foo <= 5" == str(comp)
        assert comp.compare_operator(4, 5)
        assert comp.compare_operator(5, 5)
        assert not comp.compare_operator(6, 5)

    def test_greater_than(self):
        comp = filtering.GreaterThan("foo", 5)
        assert "foo > 5" == str(comp)
        assert not comp.compare_operator(4, 5)
        assert not comp.compare_operator(5, 5)
        assert comp.compare_operator(6, 5)

    def test_greater_than_or_equal(self):
        comp = filtering.GreaterThanOrEqual("foo", 5)
        assert "foo >= 5" == str(comp)
        assert not comp.compare_operator(4, 5)
        assert comp.compare_operator(5, 5)
        assert comp.compare_operator(6, 5)
