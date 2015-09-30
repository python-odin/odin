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
