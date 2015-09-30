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
            [TraversalPath.parse('title'), None, filtering.Eq("Consider Phlebas")]
        )
        self.assertTrue(flt.matches(first_book))

    def test_matches_multiple_matches_resource(self):
        # Less than fiction $20 with a single author and not fantasy
        flt = filtering.Filter(
            [TraversalPath.parse('fiction'), None, filtering.Eq(True)],
            [TraversalPath.parse('rrp'), None, filtering.LT(20)],
            [TraversalPath.parse('authors'), len, filtering.Eq(1)],
            [TraversalPath.parse('genre'), None, filtering.Not(filtering.Eq('fantasy'))],
        )
        self.assertTrue(flt.matches(first_book))

    def test_matches_sub_resource(self):
        flt = filtering.Filter(
            [TraversalPath.parse('publisher.name'), None, filtering.Eq("Macmillan")]
        )
        self.assertTrue(flt.matches(first_book))

    def test_find_sub_resources(self):
        flt = filtering.Filter(
            [TraversalPath.parse('fiction'), None, None]
        )
        # Some fiction?
        self.assertTrue(any(flt.matches(b) for b in library.books))
        # All fiction
        self.assertFalse(all(flt.matches(b) for b in library.books))

    def test_resource_field_does_not_exist(self):
        flt = filtering.Filter(
            [TraversalPath.parse('title'), None, "Public Library"]
        )
        self.assertFalse(flt.matches(library))
