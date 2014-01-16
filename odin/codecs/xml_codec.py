# -*- coding: utf-8 -*-
from xml import sax
import datetime
from io import StringIO
from odin import serializers
from odin import fields
from odin.fields import composite

XML_TYPES = {
    datetime.date: serializers.date_iso_format,
    datetime.time: serializers.time_iso_format,
    datetime.datetime: serializers.datetime_iso_format,
}
XML_RESOURCE_LIST_FIELDS = [composite.ListOf]
XML_RESOURCE_DICT_FIELDS = [composite.DictAs]
XML_LIST_FIELDS = [fields.ArrayField, fields.TypedArrayField]


class OdinContentHandler(sax.ContentHandler):
    def __init__(self, resource):
        self.elements = []
        self.resources = []
        self.resource = resource

    def startDocument(self):
        print("startDocument")
        self.elements = []
        self.resources = []

    def endDocument(self):
        print("endDocument")

    def startElement(self, name, attrs):
        print("startElement", name, attrs['name'] if 'name' in attrs else '')

        self.elements.append(name)

    def endElement(self, name):
        print("endElement", name)

        self.elements.pop()

    def startElementNS(self, name, qname, attrs):
        print("startElementNS", name, qname, attrs)

    def endElementNS(self, name, qname):
        print("endElementNS", name, qname)

    def characters(self, content):
        print("characters", content)

    def processingInstruction(self, target, data):
        print("processingInstruction", target, data)

    def ignorableWhitespace(self, whitespace):
        print("ignorableWhitespace", whitespace)

    def skippedEntity(self, name):
        print("skippedEntity", name)

    def startPrefixMapping(self, prefix, uri):
        print("startPrefixMapping", prefix, uri)

    def endPrefixMapping(self, prefix):
        print("endPrefixMapping", prefix)

    def setDocumentLocator(self, locator):
        print("setDocumentLocator", locator)


def load(fp, resource=None):
    handler = OdinContentHandler(resource)
    sax.parse(fp, handler)


def loads(s, resource=None):
    handler = OdinContentHandler(resource)
    sax.parseString(s, handler)


def dump(fp, resource, line_ending=''):
    """
    Dump a resource to a file like object.
    :param fp: File pointer or file like object.
    :param resource: Resource to dump
    :param line_ending:
    """
    meta = resource._meta

    # Write container and any attributes
    attributes = ' '.join('%s="%s"' % (f.name, f.value_from_object(resource)) for f in meta.attribute_fields)
    if attributes:
        fp.write("<%s %s>%s" % (meta.name, attributes, line_ending))
    else:
        fp.write("<%s>%s" % (meta.name, line_ending))

    for field in resource._meta.element_fields:
        value = field.value_from_object(resource)
        if field.__class__ in XML_RESOURCE_LIST_FIELDS:
            fp.write("<%s>%s" % (field.name, line_ending))
            for v in value:
                dump(fp, v, line_ending)
            fp.write("</%s>%s" % (field.name, line_ending))

        elif field.__class__ in XML_RESOURCE_DICT_FIELDS:
            dump(fp, value, line_ending)

        else:
            if value.__class__ in XML_TYPES:
                value = XML_TYPES[value.__class__](value)
            fp.write("<%s>%s</%s>%s" % (field.name, value, field.name, line_ending))

    fp.write("</%s>%s" % (meta.name, line_ending))


def dumps(resource, **kwargs):
    """
    Dump a resource to a string.

    :param resource: Resource to dump
    :return:
    """
    f = StringIO()
    dump(f, resource, **kwargs)
    return f.getvalue()
