# -*- coding: utf-8 -*-
import unittest
from odin.mapping import helpers


class MappingHelpersTestCase(unittest.TestCase):
    def test_sum_fields(self):
        self.assertEqual(42, helpers.sum_fields(22, 20))

    def test_cat_fields(self):
        self.assertEqual("abcd", helpers.cat_fields()("ab", "cd"))
        self.assertEqual("ab-cd", helpers.cat_fields('-')("ab", "cd"))

    def test_split_field(self):
        self.assertEqual(["ab", "cd"], helpers.split_field()("ab cd"))
        self.assertEqual(["abcd"], helpers.split_field('-')("abcd"))
        self.assertEqual(["ab", "cd"], helpers.split_field('-')("ab-cd"))
        self.assertEqual(["ab", "cd", "ef"], helpers.split_field('-')("ab-cd-ef"))
        self.assertEqual(["ab", "cd-ef"], helpers.split_field('-', 1)("ab-cd-ef"))
