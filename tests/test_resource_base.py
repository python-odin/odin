# -*- coding: utf-8 -*-
import pytest
import odin
from . import resources


class TestResourceBase(object):
    def test_virtual_fields(self):
        target = resources.FromResource()

        assert ['constant_field'] == [f.name for f in target._meta.virtual_fields]

    def test_virtual_field_inheritance(self):
        target = resources.InheritedResource()

        assert ['calculated_field', 'constant_field'] == [f.name for f in target._meta.virtual_fields]

    def test_fields(self):
        target = resources.FromResource()

        assert (['title', 'count', 'child', 'children', 'excluded1', 'from_field1', 'from_field2',
                 'from_field3', 'from_field4', 'same_but_different', 'from_field_c1', 'from_field_c2',
                 'from_field_c3', 'from_field_c4', 'not_auto_c5', 'comma_separated_string'] ==
                [f.name for f in target._meta.fields])

    def test_field_inheritance(self):
        target = resources.InheritedResource()

        assert (['name', 'title', 'count', 'child', 'children', 'excluded1', 'from_field1', 'from_field2',
                 'from_field3', 'from_field4', 'same_but_different', 'from_field_c1', 'from_field_c2',
                 'from_field_c3', 'from_field_c4', 'not_auto_c5', 'comma_separated_string'] ==
                [f.name for f in target._meta.fields])

    def test_field_multi_inheritance(self):
        target = resources.MultiInheritedResource()

        assert (['name', 'title', 'count', 'child', 'children', 'excluded1', 'from_field1', 'from_field2',
                 'from_field3', 'from_field4', 'same_but_different', 'from_field_c1', 'from_field_c2',
                 'from_field_c3', 'from_field_c4', 'not_auto_c5', 'comma_separated_string'] ==
                [f.name for f in target._meta.fields])

    def test_key_field_does_not_exist(self):
        """Ensure an exception is raised if specified key_field is not a member of the resource"""
        with pytest.raises(AttributeError):
            class BadResource(odin.Resource):
                class Meta:
                    key_field_name = 'missing_field'

                field_1 = odin.StringField()
