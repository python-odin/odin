# -*- coding: utf-8 -*-
import os
import unittest
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


class CsvResourceReaderTestCase(unittest.TestCase):
    def test_valid(self):
        with open(os.path.join(FIXTURE_PATH_ROOT, "libary-valid.csv")) as f:
            books = [book for book in ResourceReader(f, Book)]

        self.assertEqual(6, len(books))
        self.assertEqual("Consider Phlebas", books[0].title)

    def test_invalid(self):
        with open(os.path.join(FIXTURE_PATH_ROOT, "libary-invalid.csv")) as f:

            with self.assertRaises(odin.exceptions.ValidationError):
                books = [book for book in ResourceReader(f, Book)]
