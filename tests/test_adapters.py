# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from odin import adapters
from odin.utils import field_iter_items
from .resources import *


class ResourceOptionsAdapterTestCase(unittest.TestCase):
    def test_repr(self):
        options = adapters.ResourceAdapter(Book())._meta

        self.assertEqual('<Options Adapter for library.Book>', repr(options))

    def test_attribute_fields(self):
        options = adapters.ResourceAdapter(Book())._meta

        self.assertListEqual(['fiction'], [f.name for f in options.attribute_fields])

    def test_elements_fields(self):
        options = adapters.ResourceAdapter(Book())._meta

        self.assertListEqual(
            ['title', 'num_pages', 'rrp', 'genre', 'published', 'authors', 'publisher'],
            [f.name for f in options.element_fields]
        )

    def test_attribute_proxying(self):
        options = adapters.ResourceAdapter(Book())._meta

        self.assertEqual("Book", options.verbose_name)


class ResourceAdapterTestCase(unittest.TestCase):
    def test_field_proxy(self):
        target = adapters.ResourceAdapter(Book(title="Foo"))

        self.assertEqual('Foo', target.title,)

    def test_include_fields(self):
        book = Book(title="Foo", rrp=123.45, num_pages=10, fiction=True)

        target = adapters.ResourceAdapter(book, include=('title', 'rrp'))

        self.assertListEqual(['rrp', 'title'], sorted(target._meta.field_map.keys()))

    def test_exclude_fields(self):
        book = Book(title="Foo", rrp=123.45, num_pages=10, fiction=True)

        target = adapters.ResourceAdapter(book, exclude=('title', 'rrp'))

        self.assertListEqual(
            ['authors', 'fiction', 'genre', 'num_pages', 'published', 'publisher'],
            sorted(target._meta.field_map.keys()))

    def test_repr(self):
        target = adapters.ResourceAdapter(Book(title="Foo"))

        self.assertEqual('<ResourceAdapter: library.Book resource adapter>', repr(target))

    def test_iter(self):
        book = Book(title="Foo", rrp=123.45, num_pages=10, fiction=True)
        target = adapters.ResourceAdapter(book)

        actual = list((f.name, str(v)) for f, v in field_iter_items(target))
        self.assertListEqual([
            ('title', 'Foo'),
            ('num_pages', '10'),
            ('rrp', '123.45'),
            ('fiction', 'True'),
            ('genre', 'None'),
            ('published', '[]'),
            ('authors', '[]'),
            ('publisher', 'None')], actual)

    def test_to_dict(self):
        publisher = Publisher()
        book = Book(title="Foo", rrp=123.45, num_pages=10, fiction=True, publisher=publisher)
        target = adapters.ResourceAdapter(book)

        self.assertDictEqual({
            'authors': [],
            'fiction': True,
            'genre': None,
            'num_pages': 10,
            'published': [],
            'publisher': publisher,
            'rrp': 123.45,
            'title': 'Foo'
        }, target.to_dict())
