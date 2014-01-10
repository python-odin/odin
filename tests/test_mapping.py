# -*- coding: utf-8 -*-
import unittest
import odin
from odin.exceptions import MappingSetupError, MappingExecutionError
from resources import *


class FakeFromResource(odin.Resource):
    title = odin.StringField()

class FakeToResource(odin.Resource):
    title = odin.StringField()


class MappingBaseTestCase(unittest.TestCase):
    maxDiff = None

    def assertMappingEquivalent(self, a, b):
        flat_a = sorted(str(i) for i in a)
        flat_b = sorted(str(i) for i in b)
        self.assertListEqual(flat_a, flat_b)

    def test_full_mapping(self):
        self.assertMappingEquivalent([
            (('from_field1',), None, ('to_field1',)),
            (('from_field2',), int, ('to_field2',)),
            (('from_field3', 'from_field4'), sum_fields, ('to_field3',)),
            (('from_field_c1', 'from_field_c2', 'from_field_c3'), 'multi_to_one', ('to_field_c1',)),
            (('from_field_c4',), 'one_to_multi', ('to_field_c2', 'to_field_c3')),
            (('not_auto_c5',), '_not_auto_c5', ('not_auto_c5',)),
            (('count',), None, ('count',)),
            (('title',), None, ('title',)),
        ], FromToMapping._mapping_rules)

    def test_map(self):
        from_resource = FromResource(
            # Auto matched
            title="Foo",
            count="42",
            # Excluded
            excluded1=123.4,
            # Mappings
            from_field1="abc",
            from_field2="62",
            from_field3=44,
            from_field4=25,
            # Custom mappings
            from_field_c1="foo",
            from_field_c2="bar",
            from_field_c3="eek",
            from_field_c4="first-second-third",
            not_auto_c5="do something",
        )

        to_resource = from_resource.convert_to(ToResource)

        self.assertEqual('Foo', to_resource.title)
        self.assertEqual('42', to_resource.count)
        self.assertEqual(None, to_resource.excluded1)
        self.assertEqual('abc', to_resource.to_field1)
        self.assertEqual(62, to_resource.to_field2)
        self.assertEqual(69, to_resource.to_field3)
        self.assertEqual('foo-bar-eek', to_resource.to_field_c1)
        self.assertEqual('first', to_resource.to_field_c2)
        self.assertEqual('second-third', to_resource.to_field_c3)
        self.assertEqual("DO SOMETHING", to_resource.not_auto_c5)

    def test_missing_from_resource(self):
        with self.assertRaises(MappingSetupError):
            class _(odin.Mapping):
                to_resource = FakeToResource

    def test_missing_to_resource(self):
        with self.assertRaises(MappingSetupError):
            class _(odin.Mapping):
                from_resource = FakeFromResource

    def test_unknown_from_field_mappings(self):
        with self.assertRaises(MappingSetupError):
            class _(odin.Mapping):
                from_resource = FakeFromResource
                to_resource = FakeToResource

                mappings = (
                    ('unknown_field', None, 'title'),
                )

    def test_unknown_from_field_mappings_multiple(self):
        with self.assertRaises(MappingSetupError):
            class _(odin.Mapping):
                from_resource = FakeFromResource
                to_resource = FakeToResource

                mappings = (
                    (('title', 'unknown_field'), None, 'title'),
                )

    def test_unknown_from_field_custom(self):
        with self.assertRaises(MappingSetupError):
            class _(odin.Mapping):
                from_resource = FakeFromResource
                to_resource = FakeToResource

                @odin.map_field(from_field='unknown_field', to_field='title')
                def multi_to_one(self, *fields):
                    pass

    def test_bad_action_not_callable(self):
        with self.assertRaises(MappingSetupError):
            class _(odin.Mapping):
                from_resource = FakeFromResource
                to_resource = FakeToResource

                mappings = (
                    ('title', 123, 'title'),
                )

    def test_bad_action_not_defined(self):
        with self.assertRaises(MappingSetupError):
            class _(odin.Mapping):
                from_resource = FakeFromResource
                to_resource = FakeToResource

                mappings = (
                    ('title', 'do_transform', 'title'),
                )

    def test_bad_action_defined_not_callable(self):
        with self.assertRaises(MappingSetupError):
            class _(odin.Mapping):
                from_resource = FakeFromResource
                to_resource = FakeToResource

                do_transform = 123

                mappings = (
                    ('title', 'do_transform', 'title'),
                )

    def test_unknown_to_field_mappings(self):
        with self.assertRaises(MappingSetupError):
            class _(odin.Mapping):
                from_resource = FakeFromResource
                to_resource = FakeToResource

                mappings = (
                    ('title', None, 'unknown_field'),
                )

    def test_unknown_to_field_mappings_multiple(self):
        with self.assertRaises(MappingSetupError):
            class _(odin.Mapping):
                from_resource = FakeFromResource
                to_resource = FakeToResource

                mappings = (
                    ('title', None, ('title', 'unknown_field')),
                )

    def test_unknown_to_field_custom(self):
        with self.assertRaises(MappingSetupError):
            class _(odin.Mapping):
                from_resource = FakeFromResource
                to_resource = FakeToResource

                @odin.map_field(from_field='title', to_field='unknown_field')
                def multi_to_one(self, *fields):
                    pass

    def test_bad_mapping(self):
        with self.assertRaises(MappingSetupError):
            class _(odin.Mapping):
                from_resource = FakeFromResource
                to_resource = FakeToResource

                mappings = (
                    'i_forgot', None, 'tuples'
                )


class MappingTestCase(unittest.TestCase):
    def test_not_valid_from_resource(self):
        self.assertRaises(TypeError, FromToMapping, FakeFromResource())

    def test_invalid_from_value_count(self):
        with self.assertRaises(MappingExecutionError):
            target = FromToMapping(FromResource())
            target._apply_rule((('from_field_c1', 'from_field_c2'), 'one_to_multi', ('title')))

    def test_invalid_to_value_count(self):
        with self.assertRaises(MappingExecutionError):
            target = FromToMapping(FromResource(title='Test'))
            target._apply_rule((('title',), 'multi_to_one', ('from_field_c1', 'from_field_c2')))

