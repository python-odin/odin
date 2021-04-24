# -*- coding: utf-8 -*-
"""
Documentation generation from resources.
"""
import os

from odin.utils import getmeta

try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    raise ImportError("Jinja2 is required for documentation generation support.")
from odin import registration

__all__ = ('FORMAT_TEMPLATE_RST', 'FORMAT_TEMPLATE_HTML', 'dump', 'dumps')

_TEMPLATE_ROOT = os.path.join(os.path.dirname(__file__), 'templates')

# Builtin format templates
FORMAT_TEMPLATE_RST = 'odin/doc.rst'
FORMAT_TEMPLATE_HTML = 'odin/doc.html'


class ResourceDocumentation(object):
    """
    Wrapper for resources to simplify documentation generation.
    """
    def __init__(self, resource):
        self.resource = resource
        self._meta = getmeta(resource)
        self._fields = None

    @property
    def verbose_name(self):
        return self._meta.verbose_name

    @property
    def description(self):
        return self.resource.__doc__

    @property
    def resource_name(self):
        return self._meta.resource_name

    @property
    def fields(self):
        if self._fields is None:
            self._fields = sorted(({
                "name": f.name,
                "doc_text": f.doc_text,
                "verbose_name": f.verbose_name,
                "verbose_name_plural": f.verbose_name_plural,
                "choices": [c[0] for c in f.choices or []],
                "has_default": f.has_default(),
                "default": f.get_default(),
                "optional": f.null,
                "null": f.null
            } for f in self._meta.fields), key=lambda f: f['name'])
        return self._fields


def _auto_escape(template_name):
    if template_name:
        _, ext = os.path.splitext(template_name)
        return ext in ('.html', '.xhtml', '.htm', '.xml')
    return False


def dump(fp, fmt=FORMAT_TEMPLATE_RST, exclude=None, template_path=None):
    """
    Dump resource documentation as Restructured Text.

    :param fp: File pointer to write documentation to.
    :param fmt: Format template, default is restructured text (can be used with Sphinx).
    :param exclude: List of resources to exclude from generation.
    :param template_path: An additional template_path for customisation of generated documentation.

    If an additional template path is supplied it will be made the first path in the template search paths and will
    override any built in templates.
    """
    fp.write(dumps(fmt, exclude, template_path))


def dumps(fmt=FORMAT_TEMPLATE_RST, exclude=None, template_path=None):
    """
    Dump resource documentation to a string.

    :param fmt: Format template, default is restructured text (can be used with Sphinx).
    :param exclude: List of resources to exclude from generation.
    :param template_path: An additional template_path for customisation of generated documentation.
    :returns: string representation of documentation.

    If an additional template path is supplied it will be made the first path in the template search paths and will
    override any built in templates.
    """
    exclude = exclude or []

    # Get template
    search_path = (template_path, _TEMPLATE_ROOT) if template_path else _TEMPLATE_ROOT
    env = Environment(loader=FileSystemLoader(search_path), autoescape=_auto_escape, )
    template = env.get_template(fmt)

    # Build resources list
    resources = [ResourceDocumentation(r) for r in registration.cache if getmeta(r).resource_name not in exclude]

    return template.render(resources=resources)
