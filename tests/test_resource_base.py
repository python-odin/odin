# -*- coding: utf-8 -*-
import unittest
from . import resources


class TestResourceBase(unittest.TestCase):
    def test_virtual_fields(self):
        target = resources.FromResource()

        self.assertEqual(['constant_field'], [f.name for f in target._meta.virtual_fields])

    def test_virtual_field_inheritance(self):
        target = resources.InheritedResource()

        self.assertEqual(['calculated_field', 'constant_field'], [f.name for f in target._meta.virtual_fields])

    def test_fields(self):
        target = resources.FromResource()

        self.assertEqual(['title', 'count', 'child', 'children', 'excluded1', 'from_field1', 'from_field2',
                          'from_field3', 'from_field4', 'same_but_different', 'from_field_c1', 'from_field_c2',
                          'from_field_c3', 'from_field_c4', 'not_auto_c5', 'comma_separated_string'],
                         [f.name for f in target._meta.fields])

    def test_field_inheritance(self):
        target = resources.InheritedResource()

        self.assertEqual(['name', 'title', 'count', 'child', 'children', 'excluded1', 'from_field1', 'from_field2',
                          'from_field3', 'from_field4', 'same_but_different', 'from_field_c1', 'from_field_c2',
                          'from_field_c3', 'from_field_c4', 'not_auto_c5', 'comma_separated_string'],
                         [f.name for f in target._meta.fields])

    def test_field_multi_inheritance(self):
        target = resources.MultiInheritedResource()

        self.assertEqual(['name', 'title', 'count', 'child', 'children', 'excluded1', 'from_field1', 'from_field2',
                          'from_field3', 'from_field4', 'same_but_different', 'from_field_c1', 'from_field_c2',
                          'from_field_c3', 'from_field_c4', 'not_auto_c5', 'comma_separated_string'],
                         [f.name for f in target._meta.fields])
