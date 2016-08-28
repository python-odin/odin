# -*- coding: utf-8 -*-
from __future__ import absolute_import
from odin import adapters
from odin.utils import field_iter_items
from .resources import *


class TestResourceOptionsAdapter(object):
    def test_repr(self):
        options = adapters.ResourceAdapter(Book())._meta

        assert '<Options Adapter for library.Book>' == repr(options)

    def test_attribute_fields(self):
        options = adapters.ResourceAdapter(Book())._meta

        assert ['fiction'] == [f.name for f in options.attribute_fields]

    def test_elements_fields(self):
        options = adapters.ResourceAdapter(Book())._meta

        assert (
            ['title', 'isbn', 'num_pages', 'rrp', 'genre', 'published', 'authors', 'publisher'] ==
            [f.name for f in options.element_fields]
        )

    def test_attribute_proxying(self):
        options = adapters.ResourceAdapter(Book())._meta

        assert "Book" == options.verbose_name


class TestResourceAdapter(object):
    def test_field_proxy(self):
        target = adapters.ResourceAdapter(Book(title="Foo"))

        assert 'Foo' == target.title

    def test_include_fields(self):
        book = Book(title="Foo", rrp=123.45, num_pages=10, fiction=True)

        target = adapters.ResourceAdapter(book, include=('title', 'rrp'))

        assert ['rrp', 'title'] == sorted(target._meta.field_map.keys())

    def test_exclude_fields(self):
        book = Book(title="Foo", rrp=123.45, num_pages=10, fiction=True)

        target = adapters.ResourceAdapter(book, exclude=('title', 'rrp'))

        assert (
            ['authors', 'fiction', 'genre', 'isbn', 'num_pages', 'published', 'publisher'] ==
            sorted(target._meta.field_map.keys())
        )

    def test_repr(self):
        target = adapters.ResourceAdapter(Book(title="Foo"))

        assert '<ResourceAdapter: library.Book resource adapter>' == repr(target)

    def test_iter(self):
        book = Book(title="Foo", isbn='abc123', rrp=123.45, num_pages=10, fiction=True)
        target = adapters.ResourceAdapter(book)

        actual = list((f.name, str(v)) for f, v in field_iter_items(target))
        assert [
            ('title', 'Foo'),
            ('isbn', 'abc123'),
            ('num_pages', '10'),
            ('rrp', '123.45'),
            ('fiction', 'True'),
            ('genre', 'None'),
            ('published', '[]'),
            ('authors', '[]'),
            ('publisher', 'None')] == actual

    def test_to_dict(self):
        publisher = Publisher()
        book = Book(title="Foo", isbn='abc123', rrp=123.45, num_pages=10, fiction=True, publisher=publisher)
        target = adapters.ResourceAdapter(book)

        assert {
            'authors': [],
            'fiction': True,
            'genre': None,
            'num_pages': 10,
            'published': [],
            'publisher': publisher,
            'rrp': 123.45,
            'isbn': 'abc123',
            'title': 'Foo'
        } == target.to_dict()

    def test_apply_to(self):
        sources = [
            Library(name="Foo"),
            Publisher(name='Bar'),
            Library(name="Eek")
        ]
        result = adapters.ResourceAdapter.apply_to(sources, include=['name'])
        actuals = list(result)

        assert([
            {'name': 'Foo'},
            {'name': 'Bar'},
            {'name': 'Eek'}
        ] == [a.to_dict() for a in actuals])

    def test_curried(self):
        book = Book(title="Foo", isbn='abc123', rrp=123.45, num_pages=10, fiction=True, publisher=Publisher())
        SummaryAdapter = adapters.ResourceAdapter.curry(include=('title', 'rrp', 'fiction'))
        target = SummaryAdapter(book)

        assert ({
            'fiction': True,
            'rrp': 123.45,
            'title': 'Foo'
        } == target.to_dict())
