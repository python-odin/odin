# -*- coding: utf-8 -*-
import os
import unittest
from odin.codecs import xml_codec

FIXTURE_PATH_ROOT = os.path.join(os.path.dirname(__file__), "fixtures")


class XmlLoadTestCase(unittest.TestCase):
    def test_valid(self):
        with open(os.path.join(FIXTURE_PATH_ROOT, "book-valid.xml")) as f:
            xml_codec.load(f)


if __name__ == '__main__':
    with open(os.path.join(FIXTURE_PATH_ROOT, "book-valid.xml")) as f:
        xml_codec.load(f)
