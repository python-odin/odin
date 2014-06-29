# -*- coding: utf-8 -*-
import unittest
from . import resources


class TestResourceBase(unittest.TestCase):
    def test_virtual_fields(self):
        target = resources.FromResource()

        self.assertEqual(['constant_field'], [f.name for f in target._meta.virtual_fields])

    def test_virtual_field_inheritances(self):
        target = resources.InheritedResource()

        self.assertEqual(['calculated_field', 'constant_field'], [f.name for f in target._meta.virtual_fields])
