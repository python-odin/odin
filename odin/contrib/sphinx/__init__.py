# -*- coding: utf-8 -*-
from sphinx.ext.autodoc import ClassDocumenter
import odin
from odin.utils import field_iter


class ResourceDocumenter(ClassDocumenter):
    objtype = 'resource'
    directivetype = 'class'

    @classmethod
    def can_document_member(cls, member, membername, isattr, parent):
        return isinstance(member, odin.Resource)

    def document_members(self, all_members=False):
        # Jump in and document fields first
        self.document_fields()

        ClassDocumenter.document_members(self, all_members)

    def document_fields(self):
        for field in field_iter(self.object):
            self.add_line('.. py:attribute:: %s' % field.name, '<odindoc>')
            if field.doc_text:
                self.add_line('    :annotation: = %s' % field.doc_text, '<odindoc>')


def setup(app):
    app.add_autodocumenter(ResourceDocumenter)
