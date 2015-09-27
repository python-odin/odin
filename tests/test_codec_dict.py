from __future__ import absolute_import
import unittest
from odin.codecs import dict_codec
from .resources import *


class DictCodecTestCase(unittest.TestCase):
    def test_dump(self):
        in_resource = Book(
            title='Consider Phlebas',
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
            'title': 'Consider Phlebas',
            'published': [],
            'publisher': {
                'name': "Macmillan",
            },
        })
