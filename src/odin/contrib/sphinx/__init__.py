"""Sphinx integration to document resources."""

from typing import Any

from sphinx.application import Sphinx
from sphinx.ext.autodoc import (
    Documenter,
    ModuleLevelDocumenter,
    ObjectMember,
    bool_option,
)
from sphinx.util import logging

import odin
from odin.resources import ResourceBase
from odin.utils import field_iter, getmeta

logger = logging.getLogger(__package__)


def reference_to(obj):
    """Generate a reference to a resource object."""
    if hasattr(obj, "_meta"):
        return f":py:class:`{getmeta(obj).name}`"
    return obj


class ResourceDocumenter(ModuleLevelDocumenter):
    """
    Extension to ``sphinx.ext.autodoc`` to support documenting Odin resources.

    This extension supports output in two forms, class doc form (for documenting the python objects) and API form for
    documenting information about fields for use in an API document.

    Usage::

        .. autoodin-resource:: namespace.path.to.your.Resource
            :include_virtual:
            :include_validators:
            :hide_choices:

    **Options**

    ``:include_virtual:``
        Include virtual fields in the output documentation

    ``:include_validators:``
        Include a bullet point list of validators associated with each field.

    ``:hide_choices:``
        Don't include choices in documentation if a field has them.

    ``:api_documentation:``
        Generate documentation in *API form*.

    """

    objtype = "odin-resource"
    directivetype = "class"
    content_indent = ""

    option_spec = dict(
        include_virtual=bool_option,
        include_validators=bool_option,
        api_documentation=bool_option,
        hide_choices=bool_option,
        **Documenter.option_spec,
    )

    @classmethod
    def can_document_member(cls, member: Any, *_) -> bool:
        """Called to see if a member can be documented by this Documenter."""
        try:
            return isinstance(member, type) and issubclass(member, ResourceBase)
        except TypeError:
            return False

    def add_directive_header(self, _: str):
        domain = getattr(self, "domain", "py")
        directive = getattr(self, "directivetype", self.objtype)
        source_name = self.get_sourcename()

        if self.options.get("api_documentation"):
            meta = getmeta(self.object)
            name = meta.resource_name
        else:
            name = self.format_name()

        self.add_line(f".. {domain}:{directive}:: {name}", source_name)

        if self.options.noindex:
            self.add_line("   :noindex:", source_name)

    def validator_description(self, validator):
        """Generate a description of a validator."""
        try:
            return str(validator)
        except Exception as ex:
            logger.warning(
                "Failed to render validator: %s",
                ex,
                location=(self.env.docname, self.directive.lineno),
            )
            logger.debug("Error rendering validator.", exc_info=True)

    def build_field_triple(self, field) -> tuple:
        """
        Build a field triple of (name, data_type, details)

        :param field: Field to build triple from.
        :return: (name, data_type, details) of a field.

        """
        details = []
        if field.doc_text:
            details.append(field.doc_text)

        if field.has_default():
            details.append(f"\n\nDefault value: {reference_to(field.get_default())}\n")

        if not self.options.get("hide_choices") and field.choices_doc_text:
            details.append("\n\nChoices:\n")
            for value, label in field.choices_doc_text:
                details.append(f"* {value} - {label}")

        if self.options.get("include_validators") and field.validators:
            details.append("\n\nValidation rules:\n")
            for validator in field.validators:
                description = self.validator_description(validator)
                details.append(f"* {description}")

        # Generate the name of the type this field represents
        type_name = field.data_type_name
        max_length = getattr(field, "max_length", None)
        if max_length:
            type_name = f"{type_name} [{max_length}]"
        if callable(type_name):
            type_name = type_name(field)
        if isinstance(field, odin.CompositeField):
            type_name = f"{type_name} {reference_to(field.of)}"

        return (
            f"*{field.name}*" if field.null else field.name,  # Name
            reference_to(type_name or "Unknown"),  # Data-type
            "\n".join(details).split("\n"),  # Details
        )

    def get_object_members(self, want_all: bool) -> tuple[bool, ObjectMember]:
        pass  # Not required; this implementation replaces the document_members method that calls get_object_members

    def document_members(self, all_members: bool = False) -> None:
        data_table = [
            self.build_field_triple(f)
            for f in field_iter(self.object, self.options.include_virtual)
        ]

        # Generate output if there is any.
        if data_table:
            # Calculate table column widths
            name_len = 4
            data_type_len = 9
            details_len = 7
            for name, data_type, details in data_table:
                name_len = max(len(name), name_len)
                data_type_len = max(len(data_type), data_type_len)
                details_len = max(*(len(value) for value in details), details_len)
            name_len += 2  # Padding
            data_type_len += 2  # Padding
            details_len += 2  # Padding

            def add_separator(char="-"):
                self.add_line(
                    f"+{char * name_len}+{char * data_type_len}+{char * details_len}+",
                    "<odin_sphinx>",
                )

            def add_row_line(name, data_type, details):
                self.add_line(
                    f"| {name}{' ' * (name_len - len(name) - 2)} "
                    f"| {data_type}{' ' * (data_type_len - len(data_type) - 2)} "
                    f"| {details}{' ' * (details_len - len(details) - 2)} |",
                    "<odin_sphinx>",
                )

            def add_row(name, data_type, details):
                add_row_line(name, data_type, details.pop(0))
                for line in details:
                    add_row_line("", "", line)

            # Generate table
            add_separator()
            add_row("Name", "Data type", ["Details"])
            add_separator("=")
            for row in data_table:
                add_row(*row)
                add_separator()


def setup(app: Sphinx):
    """Called by Sphinx to configure an integration."""
    app.add_autodocumenter(ResourceDocumenter)
