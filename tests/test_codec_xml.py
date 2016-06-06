# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
from odin.codecs import xml_codec
from .resources import *

FIXTURE_PATH_ROOT = os.path.join(os.path.dirname(__file__), "fixtures")


class TestXmlLoad(object):
    # def test_valid(self):
    #     with open(os.path.join(FIXTURE_PATH_ROOT, "book-valid.xml")) as f:
    #         xml_codec.load(f, Library)

    def test_dumps(self):
        book = Book(
            title='Consider Phlebas & Other stories',
            isbn='0-333-45430-8',
            num_pages=471,
            rrp=19.50,
            fiction=True,
            genre="sci-fi",
            authors=[Author(name="Iain M. Banks")],
            publisher=Publisher(name="Macmillan"),
        )

        assert(
"""<Book fiction="True">
<title>Consider Phlebas &amp; Other stories</title>
<isbn>0-333-45430-8</isbn>
<num_pages>471</num_pages>
<rrp>19.5</rrp>
<genre>sci-fi</genre>
<authors>
<Author>
<name>Iain M. Banks</name>
</Author>
</authors>
<Publisher>
<name>Macmillan</name>
</Publisher>
</Book>
""" == xml_codec.dumps(book, line_ending='\n'))
