# -*- coding: utf-8 -*-
"""
Do load/dump tests on known valid and invalid documents.
"""
import os
import datetime
import pytest

from odin.codecs import json_codec
from odin import exceptions
from odin.datetimeutil import utc
from ._helpers import assertJSONEqual
from .resources import *


FIXTURE_PATH_ROOT = os.path.join(os.path.dirname(__file__), "fixtures")


class TestKitchenSink(object):
    def test_dumps_with_valid_data(self):
        book = Book(title="Consider Phlebas", isbn="0-333-45430-8", num_pages=471, rrp=19.50, genre="sci-fi", fiction=True,
                    published=datetime.datetime(1987, 1, 1, tzinfo=utc))
        book.publisher = Publisher(name="Macmillan")
        book.authors.append(Author(name="Iain M. Banks"))

        library = Library(name="Public Library", books=[book])
        actual = json_codec.dumps(library)

        assertJSONEqual("""
{
    "$": "Library",
    "name": "Public Library",
    "books": [
        {
            "$": "library.Book",
            "publisher": {
                "$": "Publisher",
                "name": "Macmillan"
            },
            "num_pages": 471,
            "isbn": "0-333-45430-8",
            "title": "Consider Phlebas",
            "authors": [
                {
                    "$": "Author",
                    "name": "Iain M. Banks"
                }
            ],
            "fiction": true,
            "published": "1987-01-01T00:00:00+00:00",
            "genre": "sci-fi",
            "rrp": 19.5
        }
    ],
    "subscribers": [],
    "book_count": 1
}
        """, actual)

    def test_full_clean_invalid_data(self):
        book = Book(title="Consider Phlebas", num_pages=471, rrp=19.50, genre="space opera", fiction=True)
        book.publisher = Publisher(name="Macmillan")
        book.authors.append(Author(name="Iain M. Banks"))

        library = Library(name="Public Library", books=[book])

        with pytest.raises(exceptions.ValidationError):
            library.full_clean()

    def test_load_valid_data(self):
        library = json_codec.load(open(os.path.join(FIXTURE_PATH_ROOT, "book-valid.json")))

        assert "Consider Phlebas" == library.books[0].title

    def test_load_invalid_data(self):
        with pytest.raises(exceptions.ValidationError):
            json_codec.load(open(os.path.join(FIXTURE_PATH_ROOT, "book-invalid.json")))
