# -*- coding: utf-8 -*-
import os
import unittest
from odin.codecs import xml_codec
from resources import *

FIXTURE_PATH_ROOT = os.path.join(os.path.dirname(__file__), "fixtures")


class XmlLoadTestCase(unittest.TestCase):
    def test_valid(self):
        with open(os.path.join(FIXTURE_PATH_ROOT, "book-valid.xml")) as f:
            xml_codec.load(f)


if __name__ == '__main__':
    # with open(os.path.join(FIXTURE_PATH_ROOT, "book-valid.xml")) as f:
    #     xml_codec.load(f)

    book = Book(
        title='Consider Phlebas & Other stories',
        num_pages=471,
        rrp=19.50,
        genre="sci-fi",
        fiction=True,
        publisher=Publisher(name="Macmillan"),
        authors=[Author(name="Iain M. Banks")]
    )
    book.full_clean()

    print(xml_codec.dumps(book, line_ending='\n'))
