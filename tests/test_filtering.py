from __future__ import absolute_import
import unittest
import os
from odin import filtering
from odin.traversal import TraversalPath
from odin.codecs import json_codec


# Open library fixture
with open(os.path.join(os.path.dirname(__file__), 'fixtures', 'library.json')) as f:
    library = json_codec.load(f)


class FilterTestCase(unittest.TestCase):
    def test_matches_single_layer(self):
        flt = filtering.Filter(
            [TraversalPath('name'), None, filtering.Eq("Tim's Library")]
        )
        self.assertTrue(flt.matches(library))

    def test_matches_count_sub_resources(self):
        flt = filtering.Filter(
            [TraversalPath('name.books'), len, filtering.GTE(2)]
        )
        self.assertTrue(flt.matches(library))

    def test_find_sub_resources(self):
        flt = filtering.Filter(
            [TraversalPath('fiction'), None, None]
        )
        self.assertTrue(any(flt.matches(b) for b in library.books))
