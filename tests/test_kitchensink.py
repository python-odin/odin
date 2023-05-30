"""
Do load/dump tests on known valid and invalid documents.
"""
import datetime

import pytest

from odin import exceptions
from odin.codecs import json_codec

from ._helpers import assertJSONEqual
from .resources import *


class TestKitchenSink:
    def test_dumps_with_valid_data(self):
        book = Book(
            title="Consider Phlebas",
            isbn="0-333-45430-8",
            num_pages=471,
            rrp=19.50,
            genre="sci-fi",
            fiction=True,
            published=datetime.datetime(1987, 1, 1, tzinfo=datetime.timezone.utc),
        )
        book.publisher = Publisher(name="Macmillan")
        book.authors.append(Author(name="Iain M. Banks"))

        library = Library(name="Public Library", books=[book])
        actual = json_codec.dumps(library)

        assertJSONEqual(
            """
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
        """,
            actual,
        )

    def test_full_clean_invalid_data(
        self,
    ):
        book = Book(
            title="Consider Phlebas",
            num_pages=471,
            rrp=19.50,
            genre="space opera",
            fiction=True,
        )
        book.publisher = Publisher(name="Macmillan")
        book.authors.append(Author(name="Iain M. Banks"))

        library = Library(name="Public Library", books=[book])

        with pytest.raises(exceptions.ValidationError):
            library.full_clean()

    def test_load_valid_data(self, fixture_path):
        with (fixture_path / "book-valid.json").open() as fp:
            library = json_codec.load(fp)

        assert "Consider Phlebas" == library.books[0].title

    def test_load_invalid_data(self, fixture_path):
        with pytest.raises(exceptions.ValidationError), (
            fixture_path / "book-invalid.json"
        ).open() as fp:
            json_codec.load(fp)

    def test_load_with_invalid_nested_data__where_full_clean_is_false(
        self, fixture_path
    ):
        """Load a nested data file where data in nested resources is in-valid.

        This test is to ensure that the nested resources are still loaded, and
        invalid data is not removed and can be reported.
        """
        with (fixture_path / "library-invalid-nested.json").open() as fp:
            library = json_codec.load(fp, full_clean=False)

        assert library.books[1].isbn is None
        assert library.books[3].rrp == "nineteen dollars fifty cents"

        with pytest.raises(exceptions.ValidationError):
            library.full_clean()
