from __future__ import print_function

from odin.fields import NOT_PROVIDED
from odin.utils import field_iter
from .base import SummaryBase
from .utils import Table


class ResourceSummary(SummaryBase):
    """
    Produce a text based summary of a resource
    """
    def __init__(self, resource, out):
        super(ResourceSummary, self).__init__(out)
        self.resource = resource

    def render(self):
        table = Table(['name', 'type', 'default', 'doc_text'])

        table.add_header(name='Name', type='Type', default='Default', doc_text='Doc Text')

        for field in field_iter(self.resource):
            table.add_row(
                name=field.name,
                type=field.__class__.__name__,
                # null=str(field.null),
                default='' if field is not NOT_PROVIDED else str(field.default),
                doc_text=field.doc_text
            )

        table.render(self.out)
