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
        flt = filtering.Filter(
            ['title', None, filtering.Eq("Consider Phlebas")]
        )
        self.assertTrue(flt.matches(first_book))

    def test_matches_multiple_matches_resource(self):
        # Less than fiction $20 with a single author and not fantasy
        flt = filtering.Filter(
            ['fiction', None, filtering.Eq(True)],
            ['rrp', None, filtering.LT(20)],
            ['authors', len, filtering.Eq(1)],
            ['genre', None, filtering.Not(filtering.Eq('fantasy'))],
        )
        self.assertTrue(flt.matches(first_book))

    def test_matches_sub_resource(self):
        flt = filtering.Filter(
            ['publisher.name', None, filtering.Eq("Macmillan")]
        )
        self.assertTrue(flt.matches(first_book))

    def test_find_sub_resources(self):
        flt = filtering.Filter(
            ['fiction', None, None]
        )
        # Some fiction?
        self.assertTrue(any(flt.matches(b) for b in library.books))
        # All fiction
        self.assertFalse(all(flt.matches(b) for b in library.books))

    def test_resource_field_does_not_exist(self):
        flt = filtering.Filter(
            ['title', None, "Public Library"]
        )
        self.assertFalse(flt.matches(library))


class OperatorTestCase(unittest.TestCase):
    def test_operator(self):
        target = filtering.Operator()
        self.assertRaises(NotImplementedError, target, 1)

    def test_not_operator(self):
        target = filtering.Not(bool)
        self.assertTrue(target(False))
        self.assertTrue(target(0))
        self.assertTrue(target(""))
        self.assertFalse(target(True))
        self.assertFalse(target(1))
        self.assertFalse(target("ABC"))

    def test_lambda_operator(self):
        target = filtering.Lambda(lambda v: bool(v))
        self.assertFalse(target(False))
        self.assertFalse(target(0))
        self.assertFalse(target(""))
        self.assertTrue(target(True))
        self.assertTrue(target(1))
        self.assertTrue(target("ABC"))

    def test_eq_operator(self):
        target = filtering.Eq("foo")
        self.assertTrue(target("foo"))
        self.assertFalse(target('bar'))
        self.assertFalse(target(None))

    def test_lt_operator(self):
        target = filtering.LT(10)
        self.assertTrue(target(1))
        self.assertFalse(target(10))
        self.assertFalse(target(11))

    def test_lte_operator(self):
        target = filtering.LTE(10)
        self.assertTrue(target(1))
        self.assertTrue(target(10))
        self.assertFalse(target(11))

    def test_gt_operator(self):
        target = filtering.GT(10)
        self.assertFalse(target(1))
        self.assertFalse(target(10))
        self.assertTrue(target(11))

    def test_gte_operator(self):
        target = filtering.GTE(10)
        self.assertFalse(target(1))
        self.assertTrue(target(10))
        self.assertTrue(target(11))

    def test_in_operator(self):
        target = filtering.In(['foo', 'bar', 1])
        self.assertTrue(target('foo'))
        self.assertTrue(target(1))
        self.assertFalse(target('eek'))
        self.assertFalse(target(2))
        self.assertFalse(target(None))

    def test_is_operator(self):
        target = filtering.Is(None)
        self.assertFalse(target('foo'))
        self.assertFalse(target(1))
        self.assertFalse(target('eek'))
        self.assertFalse(target(2))
        self.assertTrue(target(None))
