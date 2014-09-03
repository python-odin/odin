# -*- coding: utf-8 -*-
from sphinx.ext.autodoc import ClassDocumenter, bool_option
import odin
from odin.utils import field_iter


class ResourceDocumenter(ClassDocumenter):
    """
    Extension to ``sphinx.ext.autodoc`` to support documenting Odin resources.

    This extension supports output in two forms, class doc form (for documenting the python objects) and API form for
    documenting information about fields for use in an API document.

    Usage::

        .. autoodin-resource:: namespace.path.to.your.Resource


    To select API form use the *apidoc* option.

    """
    objtype = 'odin-resource'
    directivetype = 'class'

    option_spec = dict(apidoc=bool_option, **ClassDocumenter.option_spec)

    @classmethod
    def can_document_member(cls, member, membername, isattr, parent):
        return isinstance(member, odin.Resource)

    def format_signature(self):
        return '(%s)' % ', '.join('%s=%s' % (f.attname, f.get_default()) for f in field_iter(self.object))

    def add_directive_header(self, sig):
        super(ResourceDocumenter, self).add_directive_header(sig)

    def add_content(self, more_content, no_docstring=False):
        super(ResourceDocumenter, self).add_content(more_content, no_docstring)

    def document_members(self, all_members=False):
        # Jump in and document fields first
        self.document_fields()

        ClassDocumenter.document_members(self, all_members)

    def document_fields(self):
        # if self.options.apidoc:
        #     self.add_line('api...', '<odin_sphinx>')

        for field in field_iter(self.object):
            self.add_line('.. py:attribute:: %s' % field.name, '<odin_sphinx>')
            if field.doc_text:
                self.add_line('    :annotation: %s' % field.doc_text, '<odin_sphinx>')

        # "name": f.name,
        # "doc_text": f.doc_text,
        # "verbose_name": f.verbose_name,
        # "verbose_name_plural": f.verbose_name_plural,
        # "choices": [c[0] for c in f.choices or []],
        # "has_default": f.has_default(),
        # "default": f.get_default(),
        # "optional": f.null,
        # "null": f.null


def setup(app):
    app.add_autodocumenter(ResourceDocumenter)
