# -*- coding: utf-8 -*-
import pytest
import odin


class MultiPartResource(odin.Resource):
    id = odin.IntegerField()
    code = odin.StringField()
    two_parts = odin.MultiPartField(('id', 'code'), separator=':')


class TestFields(object):
    def test_multipartfield__get_value(self):
        target = MultiPartResource(id=42, code='29A')

        assert '42:29A' == target.two_parts

    def test_multipartfield__unknown_fields(self):
        with pytest.raises(AttributeError) as result:
            class BadMultiPartResource(odin.Resource):
                id = odin.IntegerField()
                two_parts = odin.MultiPartField(('id', 'code'), separator=':')

        assert str(result.value).startswith("Attribute 'code' not found")


def test_calculated_field():
    @odin.calculated_field
    def sample_field(instance):
        """
        My doc text
        """
        return 42

    assert isinstance(sample_field, odin.CalculatedField)
    assert sample_field.doc_text == "My doc text"
    assert sample_field.__get__(None, None) == 42

