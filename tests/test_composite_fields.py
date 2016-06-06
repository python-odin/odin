# -*- coding: utf-8 -*-
import pytest
import odin
from odin.exceptions import ValidationError
from odin.fields.composite import DictAs, ArrayOf, DictOf


class ExampleResource(odin.Resource):
    name = odin.StringField()


class TestFields(object):
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
        with pytest.raises(TypeError):
            DictAs("an item")

    def test_dictas_1(self):
        f = DictAs(ExampleResource)
        pytest.raises(ValidationError, f.clean, None)
        pytest.raises(ValidationError, f.clean, 'abc')
        pytest.raises(ValidationError, f.clean, 123)
        pytest.raises(ValidationError, f.clean, {})
        pytest.raises(ValidationError, f.clean, {'$': 'tests.test_composite_fields.ExampleResource'})
        self.assertResourceEqual(ExampleResource(name='foo'), f.clean({'name': 'foo'}))
        self.assertResourceEqual(ExampleResource(name='foo'), f.clean({
            '$': 'tests.test_composite_fields.ExampleResource', 'name': 'foo'}))

    def test_dictas_2(self):
        f = DictAs(ExampleResource, null=True)
        assert f.clean(None) is None
        pytest.raises(ValidationError, f.clean, 'abc')
        pytest.raises(ValidationError, f.clean, 123)
        pytest.raises(ValidationError, f.clean, {})
        pytest.raises(ValidationError, f.clean, {'$': 'tests.test_composite_fields.ExampleResource'})
        self.assertResourceEqual(ExampleResource(name='foo'), f.clean({'name': 'foo'}))
        self.assertResourceEqual(ExampleResource(name='foo'), f.clean({
            '$': 'tests.test_composite_fields.ExampleResource', 'name': 'foo'}))

    # ArrayOf #################################################################

    def test_arrayof_1(self):
        f = ArrayOf(ExampleResource)
        pytest.raises(ValidationError, f.clean, None)
        pytest.raises(ValidationError, f.clean, 'abc')
        pytest.raises(ValidationError, f.clean, 123)
        pytest.raises(ValidationError, f.clean, {})
        pytest.raises(ValidationError, f.clean, {'$': 'tests.test_composite_fields.ExampleResource'})
        pytest.raises(ValidationError, f.clean, [None])
        self.assertResourceListEqual([], f.clean([]))
        self.assertResourceListEqual([ExampleResource(name='foo')], f.clean([{'name': 'foo'}]))
        self.assertResourceListEqual([ExampleResource(name='foo')], f.clean([{
            '$': 'tests.test_composite_fields.ExampleResource', 'name': 'foo'}]))

    def test_arrayof_2(self):
        f = ArrayOf(ExampleResource, null=True)
        assert f.clean(None) is None
        pytest.raises(ValidationError, f.clean, 'abc')
        pytest.raises(ValidationError, f.clean, 123)
        pytest.raises(ValidationError, f.clean, {})
        pytest.raises(ValidationError, f.clean, {'$': 'tests.test_composite_fields.ExampleResource'})
        pytest.raises(ValidationError, f.clean, [None])
        self.assertResourceListEqual([], f.clean([]))
        self.assertResourceListEqual([ExampleResource(name='foo')], f.clean([{'name': 'foo'}]))
        self.assertResourceListEqual([ExampleResource(name='foo')], f.clean([{
            '$': 'tests.test_composite_fields.ExampleResource', 'name': 'foo'}]))

    def test_arrayof_3(self):
        f = ArrayOf(ExampleResource, empty=False)
        pytest.raises(ValidationError, f.clean, None)
        pytest.raises(ValidationError, f.clean, 'abc')
        pytest.raises(ValidationError, f.clean, 123)
        pytest.raises(ValidationError, f.clean, {})
        pytest.raises(ValidationError, f.clean, {'$': 'tests.test_composite_fields.ExampleResource'})
        pytest.raises(ValidationError, f.clean, [None])
        pytest.raises(ValidationError, f.clean, [])
        self.assertResourceListEqual([ExampleResource(name='foo')], f.clean([{'name': 'foo'}]))
        self.assertResourceListEqual([ExampleResource(name='foo')], f.clean([{
            '$': 'tests.test_composite_fields.ExampleResource', 'name': 'foo'}]))

    # DictOf #################################################################

    def test_dictof_1(self):
        f = DictOf(ExampleResource)
        pytest.raises(ValidationError, f.clean, None)
        pytest.raises(ValidationError, f.clean, 'abc')
        pytest.raises(ValidationError, f.clean, 123)
        pytest.raises(ValidationError, f.clean, [])
        pytest.raises(ValidationError, f.clean, {'$': 'tests.test_composite_fields.ExampleResource'})
        pytest.raises(ValidationError, f.clean, {'abc': None})
        self.assertResourceDictEqual({}, f.clean({}))
        self.assertResourceDictEqual({'foo': ExampleResource(name='foo')}, f.clean({'foo': {'name': 'foo'}}))
        self.assertResourceDictEqual({'foo': ExampleResource(name='foo')}, f.clean({'foo': {
            '$': 'tests.test_composite_fields.ExampleResource', 'name': 'foo'}}))

    def test_dictof_2(self):
        f = DictOf(ExampleResource, null=True)
        assert f.clean(None) is None
        pytest.raises(ValidationError, f.clean, 'abc')
        pytest.raises(ValidationError, f.clean, 123)
        pytest.raises(ValidationError, f.clean, [])
        pytest.raises(ValidationError, f.clean, {'$': 'tests.test_composite_fields.ExampleResource'})
        pytest.raises(ValidationError, f.clean, {'abc': None})
        self.assertResourceDictEqual({}, f.clean({}))
        self.assertResourceDictEqual({'foo': ExampleResource(name='foo')}, f.clean({'foo': {'name': 'foo'}}))
        self.assertResourceDictEqual({'foo': ExampleResource(name='foo')}, f.clean({'foo': {
            '$': 'tests.test_composite_fields.ExampleResource', 'name': 'foo'}}))

    def test_dictof_3(self):
        f = DictOf(ExampleResource, empty=False)
        pytest.raises(ValidationError, f.clean, None)
        pytest.raises(ValidationError, f.clean, 'abc')
        pytest.raises(ValidationError, f.clean, 123)
        pytest.raises(ValidationError, f.clean, [])
        pytest.raises(ValidationError, f.clean, {'$': 'tests.test_composite_fields.ExampleResource'})
        pytest.raises(ValidationError, f.clean, {'abc': None})
        pytest.raises(ValidationError, f.clean, {})
        self.assertResourceDictEqual({'foo': ExampleResource(name='foo')}, f.clean({'foo': {'name': 'foo'}}))
        self.assertResourceDictEqual({'foo': ExampleResource(name='foo')}, f.clean({'foo': {
            '$': 'tests.test_composite_fields.ExampleResource', 'name': 'foo'}}))

    def test_dictof_key_choices(self):
        f = DictOf(ExampleResource, null=True, key_choices=(
            ('foo', 'Foo'),
            (None, 'None'),
        ))
        pytest.raises(ValidationError, f.clean, {'eek': ExampleResource(name='foo')})
        self.assertResourceDictEqual({'foo': ExampleResource(name='foo')}, f.clean({'foo': {'name': 'foo'}}))
