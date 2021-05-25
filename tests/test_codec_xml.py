# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
from datetime import date

from odin.codecs import xml_codec
from .resources import *

FIXTURE_PATH_ROOT = os.path.join(os.path.dirname(__file__), "fixtures")


class Summary(odin.Resource):
    format = odin.StringField(is_attribute=True)
    content = xml_codec.TextField()


class XMLBook(LibraryBook):
    title = odin.StringField()
    isbn = odin.StringField(key=True)
    num_pages = odin.IntegerField()
    rrp = odin.FloatField(default=20.4, use_default_if_not_provided=True)
    fiction = odin.BooleanField(is_attribute=True)
    genre = odin.StringField(
        choices=(
            ("sci-fi", "Science Fiction"),
            ("fantasy", "Fantasy"),
            ("biography", "Biography"),
            ("others", "Others"),
            ("computers-and-tech", "Computers & technology"),
        )
    )
    published = odin.TypedArrayField(odin.DateField())
    authors = odin.ArrayOf(Author, use_container=True)
    publisher = odin.DictAs(Publisher, null=True)
    summary = odin.DictAs(Summary)


class TestXmlLoad(object):
    def test_dumps(self):
        book = XMLBook(
            title="Consider Phlebas & Other stories",
            isbn="0-333-45430-8",
            num_pages=471,
            rrp=19.50,
            fiction=True,
            genre="sci-fi",
            published=[date(1987, 1, 1)],
            authors=[Author(name="Iain M. Banks")],
            publisher=Publisher(name="Macmillan"),
            summary=Summary(
                format="text/plain",
                content="The Culture and the Idiran Empire are at war in a galaxy-spanning conflict.",
            ),
        )

        assert """<XMLBook fiction="True">
<title>Consider Phlebas &amp; Other stories</title>
<isbn>0-333-45430-8</isbn>
<num_pages>471</num_pages>
<rrp>19.5</rrp>
<genre>sci-fi</genre>
<published>1987-01-01</published>
<authors>
<Author>
<name>Iain M. Banks</name>
</Author>
</authors>
<Publisher>
<name>Macmillan</name>
</Publisher>
<Summary format="text/plain">
The Culture and the Idiran Empire are at war in a galaxy-spanning conflict.
</Summary>
</XMLBook>
""" == xml_codec.dumps(
            book, line_ending="\n"
        )
