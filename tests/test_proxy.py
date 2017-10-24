import pytest

from odin.resources import create_resource_from_dict
from odin.utils import getmeta
from odin import proxy

from .resources import Book, BookProxy


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
        proxy.FieldProxyDescriptor(readonly=True).contribute_to_class(Target, 'eek')

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

    def test_set__readonly(self, proxy_obj):
        shadow = MockObject(foo='123', eek='789')
        target = proxy_obj(shadow)

        with pytest.raises(AttributeError):
            target.eek = 321

        assert '789' == shadow.eek


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

    def test_repr(self):
        class SampleProxy(proxy.ResourceProxy):
            class Meta:
                resource = Book

        assert '<Proxy of <Options for library.Book>>' == repr(getmeta(SampleProxy))

    def test_field_sorting(self):
        class SampleProxy(proxy.ResourceProxy):
            class Meta:
                field_sorting = True
                resource = Book

        assert [f.attname for f in getmeta(SampleProxy).fields] == [
            'title', 'isbn', 'num_pages', 'rrp', 'fiction', 'genre', 'published', 'authors', 'publisher']

    def test_field_sorting__custom(self):
        class SampleProxy(proxy.ResourceProxy):
            class Meta:
                def field_sorting(fields):
                    return sorted(fields, key=lambda f: f.attname)
                resource = Book

        assert [f.attname for f in getmeta(SampleProxy).fields] == [
            'authors', 'fiction', 'genre', 'isbn', 'num_pages', 'published', 'publisher', 'rrp', 'title']


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
        ('key_field_names', ('isbn',)),
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

    def test_proxy__iterable(self):
        actual = [Book(title='1984'), Book(title='1985 - The man strikes back'), Book(title='1986 - Return of the man')]
        target = BookProxy.proxy(actual)

        assert isinstance(target, proxy.ResourceProxyIter)
        assert ['1984', '1985 - The man strikes back', '1986 - Return of the man'] == [t.title for t in target]

    def test_proxy__unknown(self):
        with pytest.raises(TypeError):
            BookProxy.proxy(123)

    def test_extra_property(self):
        book = Book(rrp=256)
        target = BookProxy.proxy(book)

        assert target.expensive

    def test_create_resource_from_dict(self):
        actual = create_resource_from_dict({'title': '1984', 'isbn': '1234567', 'num_pages': 1}, BookProxy)

        assert actual.title == '1984'
