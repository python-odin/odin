# -*- coding: utf-8 -*-
from __future__ import absolute_import
import datetime
import os
from odin.datetimeutil import utc
from six import BytesIO
import unittest
from odin.codecs import msgpack_codec
from .resources import *

FIXTURE_PATH_ROOT = os.path.join(os.path.dirname(__file__), "fixtures")


class MsgPackCodecTestCase(unittest.TestCase):
    def test_dumps_and_loads(self):
        in_resource = Book(
            title='Consider Phlebas',
            num_pages=471,
            rrp=19.50,
            fiction=True,
            genre="sci-fi",
            authors=[Author(name="Iain M. Banks")],
            publisher=Publisher(name="Macmillan"),
        )

        data = msgpack_codec.dumps(in_resource)
        out_resource = msgpack_codec.loads(data)

        self.assertEqual(out_resource.title, in_resource.title)
        self.assertEqual(out_resource.num_pages, in_resource.num_pages)
        self.assertEqual(out_resource.rrp, in_resource.rrp)
        self.assertEqual(out_resource.fiction, in_resource.fiction)
        self.assertEqual(out_resource.genre, in_resource.genre)
        self.assertEqual(out_resource.authors[0].name, in_resource.authors[0].name)
        self.assertEqual(out_resource.publisher.name, in_resource.publisher.name)


    def test_dump_and_load_(self):
        in_resource = Book(
            title='Consider Phlebas',
            num_pages=471,
            rrp=19.50,
            fiction=True,
            genre="sci-fi",
            authors=[Author(name="Iain M. Banks")],
            publisher=Publisher(name="Macmillan"),
            published=[datetime.datetime(1987, 1, 1, tzinfo=utc)]
        )

        fp = BytesIO()
        msgpack_codec.dump(in_resource, fp)

        fp.seek(0)
        out_resource = msgpack_codec.load(fp)

        self.assertEqual(out_resource.title, in_resource.title)
        self.assertEqual(out_resource.num_pages, in_resource.num_pages)
        self.assertEqual(out_resource.rrp, in_resource.rrp)
        self.assertEqual(out_resource.fiction, in_resource.fiction)
        self.assertEqual(out_resource.genre, in_resource.genre)
        self.assertEqual(out_resource.authors[0].name, in_resource.authors[0].name)
        self.assertEqual(out_resource.publisher.name, in_resource.publisher.name)
        self.assertEqual(out_resource.published[0], in_resource.published[0])
