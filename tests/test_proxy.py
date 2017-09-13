import pytest
from odin.utils import getmeta

import odin

from odin import proxy
from .resources import Book


class MockObject(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class TestFieldProxyDescriptor(object):
    @pytest.fixture
    def proxy_obj(self):
        class Target(object):
            def __init__(self, shadow):
                self._shadow = shadow

        proxy.FieldProxyDescriptor().contribute_to_class(Target, 'foo')
        proxy.FieldProxyDescriptor().contribute_to_class(Target, 'bar')

        return Target

    def test_get(self, proxy_obj):
        target = proxy_obj(MockObject(foo='123', eek='789'))

        assert target.foo == '123'
        with pytest.raises(AttributeError):
            print(target.bar)

    def test_set(self, proxy_obj):
        shadow = MockObject(foo='123', eek='789')
        target = proxy_obj(shadow)

        target.foo = '321'
        target.bar = '654'

        assert shadow.foo == '321'
        assert shadow.bar == '654'


class TestFilterFields(object):
    @pytest.fixture
    def field_map(self):
        return getmeta(Book).field_map

    @pytest.mark.parametrize('kwargs, expected_fields, expected_readonly', (
        ({}, {'title', 'isbn', 'num_pages', 'rrp', 'fiction', 'genre', 'published', 'publisher', 'authors'}, set()),
        ({'include': ['title', 'isbn']}, {'title', 'isbn'}, set()),
        ({'exclude': ['rrp', 'fiction', 'genre', 'publisher', 'authors']}, {'title', 'isbn', 'num_pages', 'published'}, set()),
        ({'include': ['title', 'isbn'], 'exclude': ['isbn', 'rrp', 'fiction', 'genre']}, {'title'}, set()),
        ({'include': ['title', 'isbn'], 'readonly': ['isbn']}, {'title', 'isbn'}, {'isbn'}),
        ({'include': ['title', 'isbn'], 'readonly': ['isbn', 'rrp']}, {'title', 'isbn'}, {'isbn'}),
        ({'include': ['title', 'isbn', 'rrp'], 'exclude': ['rrp'], 'readonly': ['isbn', 'rrp']}, {'title', 'isbn'}, {'isbn'}),
    ))
    def test_filtering(self, field_map, kwargs, expected_fields, expected_readonly):
        fields, readonly = proxy.filter_fields(field_map, **kwargs)

        fields = {field.attname for field in fields}
        readonly = {field.attname for field in readonly}

        assert fields == expected_fields
        assert readonly == expected_readonly
