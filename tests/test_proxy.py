import pytest

from odin.utils import getmeta
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
        ({}, ['title', 'isbn', 'num_pages', 'rrp', 'fiction', 'genre', 'published', 'authors', 'publisher'], []),
        ({'include': ['title', 'isbn']}, ['title', 'isbn'], []),
        ({'exclude': ['rrp', 'fiction', 'genre', 'publisher', 'authors']}, ['title', 'isbn', 'num_pages', 'published'], []),
        ({'include': ['title', 'isbn'], 'exclude': ['isbn', 'rrp', 'fiction', 'genre']}, ['title'], []),
        ({'include': ['title', 'isbn'], 'readonly': ['isbn']}, ['title', 'isbn'], ['isbn']),
        ({'include': ['title', 'isbn'], 'readonly': ['isbn', 'rrp']}, ['title', 'isbn'], ['isbn']),
        ({'include': ['title', 'isbn', 'rrp'], 'exclude': ['rrp'], 'readonly': ['isbn', 'rrp']}, ['title', 'isbn'], ['isbn']),
    ))
    def test_filtering(self, field_map, kwargs, expected_fields, expected_readonly):
        fields, readonly = proxy.filter_fields(field_map, **kwargs)

        fields = [field.attname for field in fields]
        readonly = [field.attname for field in readonly]

        assert fields == expected_fields
        assert readonly == expected_readonly


class BookProxy(proxy.ResourceProxy):
    class Meta:
        resource = Book
        include = ('title', 'isbn', 'num_pages', 'rrp')
        verbose_name = 'Book Summary'
        namespace = 'the.other.library'

    @property
    def expensive(self):
        return self.rrp > 200


class TestResourceProxyMeta(object):
    def test_no_meta(self):
        with pytest.raises(AttributeError):
            class SampleProxy(proxy.ResourceProxy):
                pass

    def test_no_resource(self):
        with pytest.raises(AttributeError):
            class SampleProxy(proxy.ResourceProxy):
                class Meta:
                    pass


class TestResourceProxyOptions(object):
    def test_options_type(self):
        actual = getmeta(BookProxy)
        assert isinstance(actual, proxy.ResourceProxyOptions)

    def test_invalid_option(self):
        with pytest.raises(TypeError):
            class SampleProxy(proxy.ResourceProxy):
                class Meta:
                    resource = Book
                    eek = 'boo!'

    @pytest.mark.parametrize('attr, actual', (
        ('key_field_name', 'isbn'),
        ('verbose_name', 'Book Summary'),
        ('verbose_name_plural', 'Book Summarys'),
        ('include', ('title', 'isbn', 'num_pages', 'rrp')),
        ('name_space', 'the.other.library'),
    ))
    def test_options(self, attr, actual):
        target = getmeta(BookProxy)

        assert actual == getattr(target, attr)


class TestResourceProxy(object):
    def test_shadow(self):
        target = BookProxy()
        actual = target.get_shadow()

        assert isinstance(actual, Book)

    def test_proxy(self):
        actual = Book(title='1984')
        target = BookProxy.proxy(actual)

        assert target.title == '1984'
        assert actual is target.get_shadow()

    def test_extra_property(self):
        book = Book(rrp=256)
        target = BookProxy.proxy(book)

        assert target.expensive
