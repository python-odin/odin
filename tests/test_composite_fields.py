# -*- coding: utf-8 -*-
import unittest
import odin
from odin.exceptions import ValidationError
from odin.fields.composite import DictAs, ArrayOf, DictOf


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
            raise AssertionError("First is not a list")
        if not isinstance(second, list):
            raise AssertionError("Second is not a list")
        if len(first) != len(second):
            raise AssertionError("Lists are different lengths")
        for idx in range(len(first)):
            self.assertResourceEqual(first[idx], second[idx])

    def assertResourceDictEqual(self, first, second):
        if not isinstance(first, dict):
            raise AssertionError("First is not a dict")
        if not isinstance(second, dict):
            raise AssertionError("Second is dict")
        if len(first) != len(second):
            raise AssertionError("Dicts are different lengths")
        for key in first.keys():
            self.assertResourceEqual(first[key], second[key])

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
        self.assertRaises(ValidationError, f.clean, {'$': 'tests.test_composite_fields.ExampleResource'})
        self.assertResourceEqual(ExampleResource(name='foo'), f.clean({'name': 'foo'}))
        self.assertResourceEqual(ExampleResource(name='foo'), f.clean({
            '$': 'tests.test_composite_fields.ExampleResource', 'name': 'foo'}))

    def test_dictas_2(self):
        f = DictAs(ExampleResource, null=True)
        self.assertEqual(None, f.clean(None))
        self.assertRaises(ValidationError, f.clean, 'abc')
        self.assertRaises(ValidationError, f.clean, 123)
        self.assertRaises(ValidationError, f.clean, {})
        self.assertRaises(ValidationError, f.clean, {'$': 'tests.test_composite_fields.ExampleResource'})
        self.assertResourceEqual(ExampleResource(name='foo'), f.clean({'name': 'foo'}))
        self.assertResourceEqual(ExampleResource(name='foo'), f.clean({
            '$': 'tests.test_composite_fields.ExampleResource', 'name': 'foo'}))

    # ArrayOf #################################################################

    def test_arrayof_1(self):
        f = ArrayOf(ExampleResource)
        self.assertRaises(ValidationError, f.clean, None)
        self.assertRaises(ValidationError, f.clean, 'abc')
        self.assertRaises(ValidationError, f.clean, 123)
        self.assertRaises(ValidationError, f.clean, {})
        self.assertRaises(ValidationError, f.clean, {'$': 'tests.test_composite_fields.ExampleResource'})
        self.assertRaises(ValidationError, f.clean, [None])
        self.assertResourceListEqual([ExampleResource(name='foo')], f.clean([{'name': 'foo'}]))
        self.assertResourceListEqual([ExampleResource(name='foo')], f.clean([{
            '$': 'tests.test_composite_fields.ExampleResource', 'name': 'foo'}]))

    def test_arrayof_2(self):
        f = ArrayOf(ExampleResource, null=True)
        self.assertEqual(None, f.clean(None))
        self.assertRaises(ValidationError, f.clean, 'abc')
        self.assertRaises(ValidationError, f.clean, 123)
        self.assertRaises(ValidationError, f.clean, {})
        self.assertRaises(ValidationError, f.clean, {'$': 'tests.test_composite_fields.ExampleResource'})
        self.assertRaises(ValidationError, f.clean, [None])
        self.assertResourceListEqual([ExampleResource(name='foo')], f.clean([{'name': 'foo'}]))
        self.assertResourceListEqual([ExampleResource(name='foo')], f.clean([{
            '$': 'tests.test_composite_fields.ExampleResource', 'name': 'foo'}]))

    # DictOf #################################################################

    def test_dictof_1(self):
        f = DictOf(ExampleResource)
        self.assertRaises(ValidationError, f.clean, None)
        self.assertRaises(ValidationError, f.clean, 'abc')
        self.assertRaises(ValidationError, f.clean, 123)
        self.assertRaises(ValidationError, f.clean, [])
        self.assertRaises(ValidationError, f.clean, {'$': 'tests.test_composite_fields.ExampleResource'})
        self.assertRaises(ValidationError, f.clean, {'abc': None})
        self.assertResourceDictEqual({'foo': ExampleResource(name='foo')}, f.clean({'foo': {'name': 'foo'}}))
        self.assertResourceDictEqual({'foo': ExampleResource(name='foo')}, f.clean({'foo': {
            '$': 'tests.test_composite_fields.ExampleResource', 'name': 'foo'}}))

    def test_dictof_2(self):
        f = DictOf(ExampleResource, null=True)
        self.assertEqual(None, f.clean(None))
        self.assertRaises(ValidationError, f.clean, 'abc')
        self.assertRaises(ValidationError, f.clean, 123)
        self.assertRaises(ValidationError, f.clean, [])
        self.assertRaises(ValidationError, f.clean, {'$': 'tests.test_composite_fields.ExampleResource'})
        self.assertRaises(ValidationError, f.clean, {'abc': None})
        self.assertResourceDictEqual({'foo': ExampleResource(name='foo')}, f.clean({'foo': {'name': 'foo'}}))
        self.assertResourceDictEqual({'foo': ExampleResource(name='foo')}, f.clean({'foo': {
            '$': 'tests.test_composite_fields.ExampleResource', 'name': 'foo'}}))
