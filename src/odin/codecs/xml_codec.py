# -*- coding: utf-8 -*-
from xml import sax


class OdinContentHandler(sax.ContentHandler):
    pass


def load(fp, resource=None):
    handler = OdinContentHandler()
    sax.parse(fp, handler)


def loads(s, resource=None):
    handler = OdinContentHandler()
    sax.parseString(s, handler)
