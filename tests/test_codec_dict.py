from __future__ import absolute_import
import unittest
import datetime
from odin.codecs import dict_codec
from odin.datetimeutil import utc
from .resources import *


class DictCodecTestCase(unittest.TestCase):
    def test_dump(self):
        in_resource = Book(
            title='Consider Phlebas',
            isbn='0-333-45430-8',
            num_pages=471,
            rrp=19.50,
            fiction=True,
            genre="sci-fi",
            authors=[Author(name="Iain M. Banks")],
            publisher=Publisher(name="Macmillan"),
        )

        actual = dict_codec.dump(in_resource)
        self.assertDictEqual(actual, {
            '$': 'library.Book',
            'authors': [{
                '$': 'Author',
                'name': "Iain M. Banks",
            }],
            'fiction': True,
            'genre': "sci-fi",
            'num_pages': 471,
            'rrp': 19.50,
            'isbn': '0-333-45430-8',
            'title': 'Consider Phlebas',
            'published': [],
            'publisher': {
                '$': 'Publisher',
                'name': "Macmillan",
            },
        })

    def test_dump_no_type_field(self):
        in_resource = Book(
            title='Consider Phlebas',
            isbn='0-333-45430-8',
            num_pages=471,
            rrp=19.50,
            fiction=True,
            genre="sci-fi",
            authors=[Author(name="Iain M. Banks")],
            publisher=Publisher(name="Macmillan"),
        )

        actual = dict_codec.dump(in_resource, include_type_field=False)
        self.assertDictEqual(actual, {
            'authors': [{
                'name': "Iain M. Banks",
            }],
            'fiction': True,
            'genre': "sci-fi",
            'num_pages': 471,
            'rrp': 19.50,
            'isbn': '0-333-45430-8',
            'title': 'Consider Phlebas',
            'published': [],
            'publisher': {
                'name': "Macmillan",
            },
        })

    def test_dump_and_load_(self):
        in_resource = Book(
            title='Consider Phlebas',
            isbn='0-333-45430-8',
            num_pages=471,
            rrp=19.50,
            fiction=True,
            genre="sci-fi",
            authors=[Author(name="Iain M. Banks")],
            publisher=Publisher(name="Macmillan"),
            published=[datetime.datetime(1987, 1, 1, tzinfo=utc)]
        )

        d = dict_codec.dump(in_resource)
        out_resource = dict_codec.load(d)

        self.assertEqual(out_resource.title, in_resource.title)
        self.assertEqual(out_resource.isbn, in_resource.isbn)
        self.assertEqual(out_resource.num_pages, in_resource.num_pages)
        self.assertEqual(out_resource.rrp, in_resource.rrp)
        self.assertEqual(out_resource.fiction, in_resource.fiction)
        self.assertEqual(out_resource.genre, in_resource.genre)
        self.assertEqual(out_resource.authors[0].name, in_resource.authors[0].name)
        self.assertEqual(out_resource.publisher.name, in_resource.publisher.name)
        self.assertEqual(out_resource.published[0], in_resource.published[0])
