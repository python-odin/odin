import datetime
import os
from io import StringIO

import pytest

from odin.codecs import toml_codec
from odin.exceptions import CodecDecodeError, ValidationError

from . import resources_annotated
from .resources import *

FIXTURE_PATH_ROOT = os.path.join(os.path.dirname(__file__), "fixtures")


class CustomString:
    def __init__(self, s):
        self.wrapped = s


class TestTomlCodec:
    def test_dumps_and_loads(self):
        in_resource = Book(
            title="Consider Phlebas",
            isbn="0-333-45430-8",
            num_pages=471,
            rrp=19.50,
            fiction=True,
            genre="sci-fi",
            authors=[Author(name="Iain M. Banks")],
            publisher=Publisher(name="Macmillan"),
        )

        data = toml_codec.dumps(in_resource)
        out_resource = toml_codec.loads(data)

        assert out_resource.title == in_resource.title
        assert out_resource.isbn == in_resource.isbn
        assert out_resource.num_pages == in_resource.num_pages
        assert out_resource.rrp == in_resource.rrp
        assert out_resource.fiction == in_resource.fiction
        assert out_resource.genre == in_resource.genre
        assert out_resource.authors[0].name == in_resource.authors[0].name
        assert out_resource.publisher.name == in_resource.publisher.name

    def test_dump_and_load(self):
        in_resource = Book(
            title="Consider Phlebas",
            isbn="0-333-45430-8",
            num_pages=471,
            rrp=19.50,
            fiction=True,
            genre="sci-fi",
            authors=[Author(name="Iain M. Banks")],
            publisher=Publisher(name="Macmillan"),
            published=[datetime.datetime(1987, 1, 1)],
        )

        fp = StringIO()
        toml_codec.dump(in_resource, fp)

        fp.seek(0)
        out_resource = toml_codec.load(fp)

        assert out_resource.title == in_resource.title
        assert out_resource.isbn == in_resource.isbn
        assert out_resource.num_pages == in_resource.num_pages
        assert out_resource.rrp == in_resource.rrp
        assert out_resource.fiction == in_resource.fiction
        assert out_resource.genre == in_resource.genre
        assert out_resource.authors[0].name == in_resource.authors[0].name
        assert out_resource.publisher.name == in_resource.publisher.name
        assert out_resource.published[0] == in_resource.published[0]

    def test_dump_and_load__where_using_an_annotated_resource(self):
        in_resource = resources_annotated.Book(
            title="Consider Phlebas",
            isbn="0-333-45430-8",
            num_pages=471,
            rrp=19.50,
            fiction=True,
            genre="sci-fi",
            authors=[resources_annotated.Author(name="Iain M. Banks")],
            publisher=resources_annotated.Publisher(name="Macmillan"),
            published=[datetime.datetime(1987, 1, 1)],
        )

        fp = StringIO()
        toml_codec.dump(in_resource, fp)

        fp.seek(0)
        out_resource = toml_codec.load(fp)

        assert out_resource.title == in_resource.title
        assert out_resource.isbn == in_resource.isbn
        assert out_resource.num_pages == in_resource.num_pages
        assert out_resource.rrp == in_resource.rrp
        assert out_resource.fiction == in_resource.fiction
        assert out_resource.genre == in_resource.genre
        assert out_resource.authors[0].name == in_resource.authors[0].name
        assert out_resource.publisher.name == in_resource.publisher.name
        assert out_resource.published[0] == in_resource.published[0]

    def test_load__where_file_is_valid(self):
        with open(os.path.join(FIXTURE_PATH_ROOT, "book-valid.toml")) as f:
            data = toml_codec.load(f)

        assert data.books[0].isbn == "1-85723-394-8"

    def test_load__where_file_is_incorrect(self):
        """
        TOML is not formatted correctly
        """
        with pytest.raises(CodecDecodeError):
            with open(os.path.join(FIXTURE_PATH_ROOT, "book-incorrect.toml")) as f:
                toml_codec.load(f)

    def test_load__where_file_is_invalid(self):
        """
        TOML contains invalid field(s)
        """
        with pytest.raises(ValidationError):
            with open(os.path.join(FIXTURE_PATH_ROOT, "book-invalid.toml")) as f:
                toml_codec.load(f)

    def test_custom_type(self, monkeypatch):
        monkeypatch.setattr(
            toml_codec, "TOML_TYPES", {CustomString: lambda x: x.wrapped}
        )

        in_resource = Book(
            title=CustomString("Consider Phlebas"),
            isbn="0-333-45430-8",
            num_pages=471,
            rrp=19.50,
            fiction=True,
            genre="sci-fi",
            authors=[Author(name="Iain M. Banks")],
            publisher=Publisher(name="Macmillan"),
            published=[datetime.datetime(1987, 1, 1)],
        )

        data = toml_codec.dumps(in_resource)
        out_resource = toml_codec.loads(data)

        assert out_resource.title == in_resource.title.wrapped

    def test_dump__with_include_type_field(self):
        fp = StringIO()
        expected = Book(
            title="Consider Phlebas",
            isbn="0-333-45430-8",
            num_pages=471,
            rrp=19.50,
            fiction=True,
            genre="sci-fi",
            authors=[Author(name="Iain M. Banks")],
            publisher=Publisher(name="Macmillan"),
            published=[datetime.datetime(1987, 1, 1)],
        )

        toml_codec.dump(expected, fp, include_type_field=True)
        fp.seek(0)
        actual = toml_codec.load(fp)

        assert expected.title == actual.title

    def test_dumps__with_include_type_field(self):
        expected = Book(
            title="Consider Phlebas",
            isbn="0-333-45430-8",
            num_pages=471,
            rrp=19.50,
            fiction=True,
            genre="sci-fi",
            authors=[Author(name="Iain M. Banks")],
            publisher=Publisher(name="Macmillan"),
            published=[datetime.datetime(1987, 1, 1)],
        )

        data = toml_codec.dumps(expected, include_type_field=True)
        actual = toml_codec.loads(data)

        assert expected.title == actual.title
