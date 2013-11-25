# -*- coding: utf-8 -*-
import unittest
import odin
from odin.exceptions import ValidationError
from odin.fields.composite import DictAs, ArrayOf


class ExampleResource(odin.Resource):
    name = odin.StringField()


class FieldsTests(unittest.TestCase):
    def assertResourceEqual(self, first, second):
        if not first:
            raise AssertionError("First item is None")
        if not second:
            raise AssertionError("Second item is None")

        if first._meta.resource_name != second._meta.resource_name:
            raise AssertionError("Resources are different types %s != %s" % (
                first._meta.resource_name, second._meta.resource_name))

        for f in first._meta.fields:
            first_val = getattr(first, f.name)
            second_val = getattr(second, f.name)
            if first_val != second_val:
                raise AssertionError("Resource field %s does not match '%s' != '%s'" % (f.name, first_val, second_val))

    def assertResourceListEqual(self, first, second):
        if not isinstance(first, list):
            raise AssertionError("First is None")
        if not isinstance(second, list):
            raise AssertionError("Second is None")
        if len(first) != len(second):
            raise AssertionError("Arrays are different lengths")
        for idx in range(len(first)):
            self.assertResourceEqual(first[idx], second[idx])

    # DictAs ##################################################################

    def test_dictas_ensure_is_resource(self):
        with self.assertRaises(TypeError):
            DictAs("an item")

    def test_dictas_1(self):
        f = DictAs(ExampleResource)
        self.assertRaises(ValidationError, f.clean, None)
        self.assertRaises(ValidationError, f.clean, 'abc')
        self.assertRaises(ValidationError, f.clean, 123)
        self.assertRaises(ValidationError, f.clean, {})
        self.assertRaises(ValidationError, f.clean, {'$': 'test_composite_fields.ExampleResource'})
        self.assertResourceEqual(ExampleResource(name='foo'), f.clean({'name': 'foo'}))
        self.assertResourceEqual(ExampleResource(name='foo'), f.clean({
            '$': 'test_composite_fields.ExampleResource', 'name': 'foo'}))

    def test_dictas_2(self):
        f = DictAs(ExampleResource, null=True)
        self.assertEqual(None, f.clean(None))
        self.assertRaises(ValidationError, f.clean, 'abc')
        self.assertRaises(ValidationError, f.clean, 123)
        self.assertRaises(ValidationError, f.clean, {})
        self.assertRaises(ValidationError, f.clean, {'$': 'test_composite_fields.ExampleResource'})
        self.assertResourceEqual(ExampleResource(name='foo'), f.clean({'name': 'foo'}))
        self.assertResourceEqual(ExampleResource(name='foo'), f.clean({
            '$': 'test_composite_fields.ExampleResource', 'name': 'foo'}))

    # ArrayOf #################################################################

    def test_arrayof_1(self):
        f = ArrayOf(ExampleResource)
        self.assertRaises(ValidationError, f.clean, None)
        self.assertRaises(ValidationError, f.clean, 'abc')
        self.assertRaises(ValidationError, f.clean, 123)
        self.assertRaises(ValidationError, f.clean, {})
        self.assertRaises(ValidationError, f.clean, {'$': 'test_composite_fields.ExampleResource'})
        self.assertRaises(ValidationError, f.clean, [None])
        self.assertResourceListEqual([ExampleResource(name='foo')], f.clean([{'name': 'foo'}]))
        self.assertResourceListEqual([ExampleResource(name='foo')], f.clean([{
            '$': 'test_composite_fields.ExampleResource', 'name': 'foo'}]))

    def test_arrayof_2(self):
        f = ArrayOf(ExampleResource, null=True)
        self.assertEqual(None, f.clean(None))
        self.assertRaises(ValidationError, f.clean, 'abc')
        self.assertRaises(ValidationError, f.clean, 123)
        self.assertRaises(ValidationError, f.clean, {})
        self.assertRaises(ValidationError, f.clean, {'$': 'test_composite_fields.ExampleResource'})
        self.assertRaises(ValidationError, f.clean, [None])
        self.assertResourceListEqual([ExampleResource(name='foo')], f.clean([{'name': 'foo'}]))
        self.assertResourceListEqual([ExampleResource(name='foo')], f.clean([{
            '$': 'test_composite_fields.ExampleResource', 'name': 'foo'}]))
