# -*- coding: utf-8 -*-
"""
Do load/dump tests on known valid and invalid documents.
"""
import os
import unittest
import sys
import datetime
import odin
from odin.codecs import json_codec
from odin import exceptions
from odin.datetimeutil import utc

FIXTURE_PATH_ROOT = os.path.join(os.path.dirname(__file__), "fixtures")


class Author(odin.Resource):
    name = odin.StringField()

    class Meta:
        name_space = None


class Publisher(odin.Resource):
    name = odin.StringField()

    class Meta:
        name_space = None


class LibraryBook(odin.Resource):
    class Meta:
        abstract = True
        name_space = "library"


class Book(LibraryBook):
    title = odin.StringField()
    num_pages = odin.IntegerField()
    rrp = odin.FloatField()
    fiction = odin.BooleanField()
    genre = odin.StringField(choices=(
        ('sci-fi', 'Science Fiction'),
        ('fantasy', 'Fantasy'),
        ('others', 'Others'),
    ))
    published = odin.DateTimeField()
    authors = odin.ArrayOf(Author)
    publisher = odin.ObjectAs(Publisher)


class Library(odin.Resource):
    name = odin.StringField()
    books = odin.ArrayOf(LibraryBook)

    class Meta:
        name_space = None


class KitchenSinkTestCase(unittest.TestCase):
    @unittest.skipIf(sys.version_info[0] > 2, "Disabled as Python 2 and Python 3 appear to output result differently. "
                                              "This test needs a better way of determining a positive outcome.")
    def test_dumps_with_valid_data(self):
        book = Book(title="Consider Phlebas", num_pages=471, rrp=19.50, genre="sci-fi", fiction=True,
                    published=datetime.datetime(1987, 1 , 1, tzinfo=utc))
        book.publisher = Publisher(name="Macmillan")
        book.authors.append(Author(name="Iain M. Banks"))

        library = Library(name="Public Library", books=[book])

        actual = json_codec.dumps(library)
        expected = '{"books": [' \
                   '{"publisher": {"name": "Macmillan", "$": "Publisher"}, "num_pages": 471, ' \
                   '"$": "library.Book", "title": "Consider Phlebas", ' \
                   '"authors": [{"name": "Iain M. Banks", "$": "Author"}], ' \
                   '"fiction": true, "published": "1987-01-01T00:00:00.000Z", "genre": "sci-fi", "rrp": 19.5}], ' \
                   '"name": "Public Library", "$": "Library"}'

        self.assertEqual(expected, actual)

    def test_full_clean_invalid_data(self):
        book = Book(title="Consider Phlebas", num_pages=471, rrp=19.50, genre="space opera", fiction=True)
        book.publisher = Publisher(name="Macmillan")
        book.authors.append(Author(name="Iain M. Banks"))

        library = Library(name="Public Library", books=[book])

        with self.assertRaises(exceptions.ValidationError):
            library.full_clean()

    def test_load_valid_data(self):
        library = json_codec.load(open(os.path.join(FIXTURE_PATH_ROOT, "book-valid.json")))

        self.assertEqual("Consider Phlebas", library.books[0].title)

    def test_load_invalid_data(self):
        with self.assertRaises(exceptions.ValidationError):
            json_codec.load(open(os.path.join(FIXTURE_PATH_ROOT, "book-invalid.json")))
