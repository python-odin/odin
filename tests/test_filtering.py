from __future__ import absolute_import
import unittest
import os
from odin import filtering
from odin.traversal import TraversalPath
from odin.codecs import json_codec


# Open library fixture
with open(os.path.join(os.path.dirname(__file__), 'fixtures', 'library.json')) as f:
    library = json_codec.load(f)

first_book = TraversalPath.parse('books[0]').get_value(library)


class FilterTestCase(unittest.TestCase):
    def test_matches_top_level_resource(self):
        flt = filtering.Equal('title', "Consider Phlebas")
        self.assertTrue(flt(first_book))

    def test_matches_multiple_matches_resource(self):
        # Less than fiction $20 with a single author and not fantasy
        flt = filtering.And(
            filtering.Equal('fiction', True),
            filtering.LessThan('rrp', 20),
            filtering.Equal('authors', 1, len),
            filtering.NotEqual('genre', 'fantasy'),
        )
        self.assertTrue(flt(first_book))

    def test_matches_sub_resource(self):
        flt = filtering.Equal('publisher.name', 'Macmillan')
        self.assertTrue(flt(first_book))

    def test_find_sub_resources(self):
        flt = filtering.Equal('fiction', True)
        # Some fiction?
        self.assertTrue(flt.any(library.books))
        # All fiction
        self.assertFalse(flt.all(library.books))

    def test_resource_field_does_not_exist(self):
        flt = filtering.Equal('title', 'Public Library')
        self.assertFalse(flt(library))


class FilterChainTestCase(unittest.TestCase):
    def test_empty_description(self):
        flt = filtering.And()
        self.assertEqual('', str(flt))

    def test_description(self):
        flt = filtering.And(
            filtering.Equal('fiction', True),
            filtering.LessThan('rrp', 20),
        )
        self.assertEqual(
            '(fiction == True AND rrp < 20)',
            str(flt)
        )

    def test_combining_same_type(self):
        flt1 = filtering.And(
            filtering.Equal('fiction', True),
            filtering.LessThan('rrp', 20),
        )
        flt2 = filtering.And(
            filtering.Equal('authors', 1, len),
            filtering.NotEqual('genre', 'fantasy'),
        )
        flt = flt1 + flt2

        self.assertEqual(
            "(fiction == True AND rrp < 20 AND len(authors) == 1 AND genre != 'fantasy')",
            str(flt)
        )

    def test_combine_with_comparison(self):
        flt1 = filtering.And(
            filtering.Equal('fiction', True),
            filtering.LessThan('rrp', 20),
        )
        flt = flt1 + filtering.Equal('authors', 1, len)

        self.assertEqual(
            "(fiction == True AND rrp < 20 AND len(authors) == 1)",
            str(flt)
        )

    def test_combine_with_other_type(self):
        flt1 = filtering.And(
            filtering.Equal('fiction', True),
            filtering.LessThan('rrp', 20),
        )
        self.assertRaises(TypeError, lambda: flt1 + 'abc')


class FilterComparisonTestCase(unittest.TestCase):
    def test_description(self):
        comp = filtering.FilterComparison('foo', 'bar')
        comp.operator_symbols = ['%']
        self.assertEqual("foo % 'bar'", str(comp))
        comp = filtering.FilterComparison('foo', 42)
        comp.operator_symbols = ['%']
        self.assertEqual('foo % 42', str(comp))
        comp = filtering.FilterComparison('foo', 'bar', any)
        comp.operator_symbols = ['%']
        self.assertEqual("any(foo) % 'bar'", str(comp))

    def test_equal_string(self):
        comp = filtering.Equal('foo', 'bar')
        self.assertTrue(comp.compare('bar'))
        self.assertFalse(comp.compare('eek'))
        self.assertEqual("foo == 'bar'", str(comp))

    def test_equal_integer(self):
        comp = filtering.Equal('foo', 5)
        self.assertTrue(comp.compare(5))
        self.assertFalse(comp.compare(6))
        self.assertEqual('foo == 5', str(comp))

    def test_not_equal(self):
        comp = filtering.NotEqual('foo', 'bar')
        self.assertTrue(comp.compare('eek'))
        self.assertFalse(comp.compare('bar'))
        self.assertEqual("foo != 'bar'", str(comp))

    def test_less_than(self):
        comp = filtering.LessThan('foo', 5)
        self.assertTrue(comp.compare(4))
        self.assertFalse(comp.compare(5))
        self.assertFalse(comp.compare(6))
        self.assertEqual('foo < 5', str(comp))

    def test_less_than_or_equal(self):
        comp = filtering.LessThanOrEqual('foo', 5)
        self.assertTrue(comp.compare(4))
        self.assertTrue(comp.compare(5))
        self.assertFalse(comp.compare(6))
        self.assertEqual('foo <= 5', str(comp))

    def test_greater_than(self):
        comp = filtering.GreaterThan('foo', 5)
        self.assertFalse(comp.compare(4))
        self.assertFalse(comp.compare(5))
        self.assertTrue(comp.compare(6))
        self.assertEqual('foo > 5', str(comp))

    def test_greater_than_or_equal(self):
        comp = filtering.GreaterThanOrEqual('foo', 5)
        self.assertFalse(comp.compare(4))
        self.assertTrue(comp.compare(5))
        self.assertTrue(comp.compare(6))
        self.assertEqual('foo >= 5', str(comp))
