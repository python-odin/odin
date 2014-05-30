# -*- coding: utf-8 -*-
import unittest
from odin import adapters
from resources import *


class ResourceAdapterTestCase(unittest.TestCase):
    def test_field_proxy(self):
        book = Book(title="Foo")

        target = adapters.ResourceAdapter(book)

        self.assertEqual(target.title, 'Foo')


