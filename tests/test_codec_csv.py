# -*- coding: utf-8 -*-
import os
import pytest
import odin
from odin.codecs.csv_codec import ResourceReader

FIXTURE_PATH_ROOT = os.path.join(os.path.dirname(__file__), "fixtures")


class Book(odin.Resource):
    title = odin.StringField(name="Title")
    num_pages = odin.IntegerField(name="Num Pages")
    rrp = odin.FloatField(name="RRP")
    genre = odin.StringField(name="Genre", choices=(
        ('sci-fi', 'Science Fiction'),
        ('fantasy', 'Fantasy'),
        ('others', 'Others'),
    ))
    author = odin.StringField(name="Author")
    publisher = odin.StringField(name="Publisher")


class TestCsvResourceReader(object):
    def test_valid(self):
        with open(os.path.join(FIXTURE_PATH_ROOT, "libary-valid.csv")) as f:
            books = [book for book in ResourceReader(f, Book)]

        assert 6 == len(books)
        assert "Consider Phlebas" == books[0].title

    def test_invalid(self):
        with open(os.path.join(FIXTURE_PATH_ROOT, "libary-invalid.csv")) as f:
            with pytest.raises(odin.exceptions.ValidationError):
                books = [book for book in ResourceReader(f, Book)]
