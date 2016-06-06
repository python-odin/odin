from __future__ import absolute_import
import datetime
from odin.codecs import dict_codec
from odin.datetimeutil import utc
from .resources import *


class TestDictCodec(object):
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
        assert actual == {
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
        }

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
        assert actual == {
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
        }

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

        assert out_resource.title == in_resource.title
        assert out_resource.isbn == in_resource.isbn
        assert out_resource.num_pages == in_resource.num_pages
        assert out_resource.rrp == in_resource.rrp
        assert out_resource.fiction == in_resource.fiction
        assert out_resource.genre == in_resource.genre
        assert out_resource.authors[0].name == in_resource.authors[0].name
        assert out_resource.publisher.name == in_resource.publisher.name
        assert out_resource.published[0] == in_resource.published[0]
