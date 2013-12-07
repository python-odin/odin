# -*- coding: utf-8 -*-
from xml import sax


class OdinContentHandler(sax.ContentHandler):
    def startDocument(self):
        self.elements = []

    def endDocument(self):
        print "endDocument"

    def startElement(self, name, attrs):
        self.elements.append(name)

        print "startElement", name, attrs['name'] if 'name' in attrs else ''

    def endElement(self, name):
        print "endElement", name

    def startElementNS(self, name, qname, attrs):
        print "startElementNS", name, qname, attrs

    def endElementNS(self, name, qname):
        print "endElementNS", name, qname

    def characters(self, content):
        print "characters", content

    def processingInstruction(self, target, data):
        print "processingInstruction", target, data

    def ignorableWhitespace(self, whitespace):
        print "ignorableWhitespace", whitespace

    def skippedEntity(self, name):
        print "skippedEntity", name

    def startPrefixMapping(self, prefix, uri):
        print "startPrefixMapping", prefix, uri

    def endPrefixMapping(self, prefix):
        print "endPrefixMapping", prefix

    def setDocumentLocator(self, locator):
        print "setDocumentLocator", locator


def load(fp, resource=None):
    handler = OdinContentHandler()
    sax.parse(fp, handler)


def loads(s, resource=None):
    handler = OdinContentHandler()
    sax.parseString(s, handler)
