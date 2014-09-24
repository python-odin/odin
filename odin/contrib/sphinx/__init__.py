# -*- coding: utf-8 -*-
from sphinx.ext.autodoc import ClassDocumenter, bool_option, ModuleLevelDocumenter
import odin
from odin.utils import field_iter


def reference_to(obj):
    if hasattr(obj, '_meta'):
        return ":py:class:`%s`" % obj._meta.name
    return obj


class ResourceDocumenter(ModuleLevelDocumenter):
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
    content_indent = ''

    option_spec = dict(apidoc=bool_option, **ClassDocumenter.option_spec)

    @classmethod
    def can_document_member(cls, member, membername, isattr, parent):
        return isinstance(member, odin.Resource)

    def format_signature(self):
        return '(%s)' % ', '.join('%s=%s' % (f.attname, f.get_default()) for f in field_iter(self.object))

    def add_directive_header(self, sig):
        self.add_line(".. py:currentmodule:: %s" % self.object._meta.name_space, '<odin_sphinx>')
        self.add_line(".. py:class:: %s" % self.object._meta.name, '<odin_sphinx>')

    def add_content(self, more_content, no_docstring=False):
        super(ResourceDocumenter, self).add_content(more_content, no_docstring)

    def document_members(self, all_members=False):
        data_table = []

        for field in field_iter(self.object):
            details = []
            if field.doc_text:
                details.append(field.doc_text)
            if field.has_default():
                details.append("\n\nDefault value: %s\n" % reference_to(field.get_default()))
            if field.choices:
                details.append("\n\nChoices:\n")
                for value, label in field.choices:
                    details.append("* %s - %s" % (value, label))
            # if field.validators:
            #     details.append("\n\nValidation rules:\n")
            #     for value, label in field.choices:
            #         details.append("* %s - %s" % (value, label))

            # Generate the name of the type this field represents
            type_name = field.data_type_name
            if callable(type_name):
                type_name = type_name(field)
            if isinstance(field, odin.CompositeField):
                type_name = "%s %s" % (type_name, reference_to(field.of))

            data_table.append((
                "*%s*" % field.name if field.null else field.name,  # Name
                ("[%s]" if field.null else "%s") % reference_to(type_name),  # Data-type
                '\n'.join(details).split('\n')  # Details
            ))

        # Calculate table column widths
        name_len = 4
        data_type_len = 9
        details_len = 7
        for name, data_type, details in data_table:
            name_len = max(len(name), name_len)
            data_type_len = max(len(data_type), data_type_len)
            details_len = max(max(len(l) for l in details), details_len)
        name_len += 2  # Padding
        data_type_len += 2  # Padding
        details_len += 2  # Padding

        def generate_separator(char='-'):
            self.add_line("+%s+%s+%s+" % (char * name_len, char * data_type_len, char * details_len), '<odin_sphinx>')

        def generate_row_line(name, data_type, details):
            self.add_line("| %s%s | %s%s | %s%s |" % (
                name, ' ' * (name_len - len(name) - 2),
                data_type, ' ' * (data_type_len - len(data_type) - 2),
                details, ' ' * (details_len - len(details) - 2),
            ), '<odin_sphinx>')

        def add_row(name, data_type, details):
            generate_row_line(name, data_type, details.pop(0))
            for line in details:
                generate_row_line('', '', line)

        # Generate table
        generate_separator()
        add_row("Name", "Data type", ["Details"])
        generate_separator('=')
        for row in data_table:
            add_row(*row)
            generate_separator()


def setup(app):
    app.add_autodocumenter(ResourceDocumenter)
