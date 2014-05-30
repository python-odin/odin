# -*- coding: utf-8 -*-
import unittest
from odin import adapters
from resources import *


class ResourceAdapterTestCase(unittest.TestCase):
    def test_field_proxy(self):
        book = Book(title="Foo")

        target = adapters.ResourceAdapter(book)

        self.assertEqual(target.title, 'Foo')

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
