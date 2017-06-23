# -*- coding: utf-8 -*-
import os
import pytest
import odin
import odin.exceptions
from odin.codecs import csv_codec

FIXTURE_PATH_ROOT = os.path.join(os.path.dirname(__file__), "fixtures")


class Book(odin.Resource):
    title = odin.StringField(name="Title")
    num_pages = odin.IntegerField(name="Num Pages")
    rrp = odin.FloatField(name="RRP")
    genre = odin.StringField(name="Genre", choices=(
        ('sci-fi', 'Science Fiction'),
        ('fantasy', 'Fantasy'),
        ('others', 'Others'),
    ), null=True)
    author = odin.StringField(name="Author")
    publisher = odin.StringField(name="Publisher")
    language = odin.StringField(name="Language", null=True)

    def extra_attrs(self, attrs):
        self.extras = attrs


class TestCsvResourceReader(object):
    def test_valid(self):
        with open(os.path.join(FIXTURE_PATH_ROOT, "library-valid.csv")) as f:
            books = [book for book in csv_codec.ResourceReader(f, Book)]

        assert 6 == len(books)
        assert "Consider Phlebas" == books[0].title

    def test_invalid(self):
        with open(os.path.join(FIXTURE_PATH_ROOT, "library-invalid.csv")) as f:
            with pytest.raises(odin.exceptions.ValidationError):
                books = [book for book in csv_codec.ResourceReader(f, Book)]


class TestReader(object):
    def open_fixture(self, file_name):
        return open(os.path.join(FIXTURE_PATH_ROOT, file_name))

    @pytest.mark.parametrize('fixture options'.split(), (
        ('library-valid.csv', dict(includes_header=True)),
        ('library-header-alt-order.csv', dict(includes_header=True)),
        ('library-last-bad.csv', dict(includes_header=True)),
        ('library-no-header.csv', dict(includes_header=False)),
        ('library-lower-header.csv', dict(includes_header=True,
                                          ignore_header_case=True)),
        ('library-valid.csv', dict(includes_header=True, strict_fields=True)),
    ))
    def test_valid_libraries(self, fixture, options):
        with self.open_fixture(fixture) as f:
            target = csv_codec.reader(f, Book, **options)
            library = list(target)
        assert len(library) == 6
        assert [book.title for book in library] == [
            'Consider Phlebas',
            'The Moonstone',
            'Casino Royale',
            'A Clockwork Orange',
            'The Naked God',
            'Equal Rites',
        ]
        assert [book.num_pages for book in library] == [
            471, 462, 181, 139, 1256, 282,
        ]
        assert [book.rrp for book in library] == [
            19.5, 17.95, 9.95, 9.95, 19.95, 16.95,
        ]
        genres = [book.genre for book in library]
        assert (
            genres == ['sci-fi', 'others', 'others', 'others', 'sci-fi', 'fantasy']
            or
            genres == [None, None, None, None, None, None]
        )
        assert [book.author for book in library] == [
            'Iain M. Banks',
            'Wilkie Collins',
            'Ian Fleming',
            'Anthony Burgess',
            'Peter F. Hamilton',
            'Terry Pratchett',
        ]
        assert [book.publisher for book in library] == [
            'Macmillan',
            'Harper & Row',
            'Penguin Books',
            'Penguin Books',
            'Macmillan',
            'Corgi Books',
        ]
        assert [book.language for book in library] == [
            'English', '', 'English', '', 'English', 'English'
        ]

    def test_extra_fields(self):
        with self.open_fixture('library-header-alt-order.csv') as f:
            target = csv_codec.reader(f, Book, includes_header=True)
            library = list(target)

        assert all(book.extras == ['Other field'] for book in library)

    def test_headers_not_strict(self):
        with self.open_fixture('library-header-alt-order.csv') as f:
            with pytest.raises(odin.exceptions.CodecDecodeError) as result:
                csv_codec.reader(f, Book, includes_header=True, strict_fields=True)

            assert str(result.value) == 'Extra unknown fields: Else'

    def test_default_empty_value_is_none(self):
        with self.open_fixture('library-valid.csv') as f:
            target = csv_codec.reader(f, Book, includes_header=True)
            target.default_empty_value = None
            library = list(target)

        assert [book.language for book in library] == [
            'English', None, 'English', None, 'English', 'English'
        ]

    def test_error(self):
        with self.open_fixture('library-invalid.csv') as f:
            target = csv_codec.reader(f, Book, includes_header=True)

            with pytest.raises(odin.exceptions.ValidationError):
                list(target)

    def test_error_handler(self):
        errors = []

        def error_handler(_, idx):
            errors.append(idx)

        with self.open_fixture('library-invalid.csv') as f:
            target = csv_codec.reader(f, Book, includes_header=True, error_callback=error_handler)
            library = list(target)

        assert len(library) == 4
        assert len(errors) == 2
        assert errors == [3, 5]

    def test_error_handler_returns_false(self):
        with self.open_fixture('library-invalid.csv') as f:
            target = csv_codec.reader(f, Book, includes_header=True, error_callback=lambda v, i: False)

            with pytest.raises(odin.exceptions.ValidationError):
                list(target)
