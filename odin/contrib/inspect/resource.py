from __future__ import print_function

from odin.fields import NOT_PROVIDED
from odin.utils import field_iter


def max_length(value):
    return max(len(l) for l in value.split('\n'))


class ResourceSummary(object):
    """
    Produce a text based summary of a resource
    """
    def __init__(self, resource):
        self.resource = resource

    def fields(self, out):
        columns = ['name', 'type', 'default', 'doc_text']
        rows = []
        lengths = {}

        def add_row(**kwargs):
            rows.append(kwargs)
            for col, value in kwargs.items():
                length = max_length(value)
                if length > lengths.setdefault(col, 0):
                    lengths[col] = length

        add_row(name='Name', type='Type', default='Default', doc_text='Doc Text')
        for field in field_iter(self.resource):
            add_row(
                name=field.name,
                type=field.__class__.__name__,
                # null=str(field.null),
                default='' if field is not NOT_PROVIDED else str(field.default),
                doc_text=field.doc_text
            )

        def print_table(idx, padding=' ', sep='|'):
            row = idx if isinstance(idx, dict) else rows[idx]
            print('|', sep.join(
                "{}{}{}{}".format(padding, row[c], padding * (lengths[c] - len(row[c])), padding) for c in columns
            ), '|', file=out, sep='')

        print_table(0)
        print_table({c: '' for c in columns}, padding='=')
        for i in range(1, len(rows)):
            print_table(i)
        print_table({c: '' for c in columns}, padding='-')
