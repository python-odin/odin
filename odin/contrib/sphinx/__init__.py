# -*- coding: utf-8 -*-
import odin

from odin.resources import ResourceBase
from odin.utils import field_iter, getmeta
from sphinx.ext.autodoc import Documenter, ModuleLevelDocumenter, bool_option


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
            :include_virtual:
            :hide_choices:

    To select API form use the *include_virtual* option.

    """
    objtype = 'odin-resource'
    directivetype = 'class'
    content_indent = ''

    option_spec = dict(
        include_virtual=bool_option,
        include_validators=bool_option,
        hide_choices=bool_option,
        **Documenter.option_spec
    )

    @classmethod
    def can_document_member(cls, member, *_):
        return isinstance(member, ResourceBase)

    def add_directive_header(self, _):
        meta = getmeta(self.object)
        self.add_line(".. py:currentmodule:: %s" % meta.name_space, '<odin_sphinx>')
        self.add_line(".. py:class:: %s" % meta.name, '<odin_sphinx>')
        if self.options.noindex:
            self.add_line('   :noindex:', '<odin_sphinx>')

    def build_field_triple(self, field):
        """
        Build a field triple of (name, data_type, details)

        :param field: Field to build triple from.
        :return: (name, data_type, details) of a field.

        """
        details = []
        if field.doc_text:
            details.append(field.doc_text)

        if field.has_default():
            details.append("\n\nDefault value: %s\n" % reference_to(field.get_default()))

        if not self.options.hide_choices and field.choices:
            details.append("\n\nChoices:\n")
            for value, label in field.choices:
                details.append("* %s - %s" % (value, label))

        if self.options.include_validators and field.validators:
            details.append("\n\nValidation rules:\n")
            for validator in field.validators:
                details.append("* %s" % validator)

        # Generate the name of the type this field represents
        type_name = field.data_type_name
        max_length = getattr(field, 'max_length', None)
        if max_length:
            type_name = "%s [%s]" % (type_name, max_length)
        if callable(type_name):
            type_name = type_name(field)
        if isinstance(field, odin.CompositeField):
            type_name = "%s %s" % (type_name, reference_to(field.of))

        return (
            "*%s*" % field.name if field.null else field.name,  # Name
            reference_to(type_name or "Unknown"),  # Data-type
            '\n'.join(details).split('\n')  # Details
        )

    def document_members(self, all_members=False):
        data_table = [
            self.build_field_triple(f) for f in field_iter(self.object, self.options.include_virtual)
        ]

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

        def add_separator(char='-'):
            self.add_line("+%s+%s+%s+" % (
                char * name_len,
                char * data_type_len,
                char * details_len
            ), '<odin_sphinx>')

        def add_row_line(name, data_type, details):
            self.add_line("| %s%s | %s%s | %s%s |" % (
                name, ' ' * (name_len - len(name) - 2),
                data_type, ' ' * (data_type_len - len(data_type) - 2),
                details, ' ' * (details_len - len(details) - 2),
            ), '<odin_sphinx>')

        def add_row(name, data_type, details):
            add_row_line(name, data_type, details.pop(0))
            for line in details:
                add_row_line('', '', line)

        # Generate table
        add_separator()
        add_row("Name", "Data type", ["Details"])
        add_separator('=')
        for row in data_table:
            add_row(*row)
            add_separator()


def setup(app):
    app.add_autodocumenter(ResourceDocumenter)
