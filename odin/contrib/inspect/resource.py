from __future__ import absolute_import, print_function
from humanfriendly import tables
from odin.fields import NOT_PROVIDED
from odin.utils import field_iter
from .base import SummaryBase


class ResourceSummary(SummaryBase):
    """
    Produce a text based summary of a resource
    """
    def __init__(self, resource, out):
        super(ResourceSummary, self).__init__(out)
        self.resource = resource

    def render(self):
        data = []
        column_names = ('Name', 'Type', 'Default', 'Doc Text')
        for field in field_iter(self.resource):
            data.append([
                field.name,
                field.__class__.__name__,
                '' if field is not NOT_PROVIDED else str(field.default),
                field.doc_text
            ])
        self.print(tables.format_pretty_table(data, column_names))
