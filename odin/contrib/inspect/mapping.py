from __future__ import absolute_import, print_function
import six

from humanfriendly import tables

from .base import SummaryBase, resource_reference


class MappingSummary(SummaryBase):
    """
    Produce a text based summary of a mapping
    """
    def __init__(self, mapping, out):
        super(MappingSummary, self).__init__(out)
        self.mapping = mapping

    def render(self):
        mapping = self.mapping
        self.title("{}.{}".format(mapping.__module__, mapping.__name__))
        self.print('')
        self.print("From:", resource_reference(mapping.from_obj))
        self.print("To:  ", resource_reference(mapping.to_obj))
        self.print('')

        # Build mapping summary
        data = []
        column_names = ('From', 'Action', 'To', 'Options')
        for from_fields, action, to_fields, to_list, bind, skip_if_none in mapping._mapping_rules:
            # Dereference
            from_fields = from_fields or ['*Assigned*']
            to_fields = to_fields or list()
            row_count = max(len(from_fields), len(to_fields))

            # Normalise
            if len(from_fields) < row_count:
                from_fields += ['' for _ in range(row_count - len(from_fields))]
            if len(to_fields) < row_count:
                to_fields += ['' for _ in range(row_count - len(to_fields))]

            if action:
                if not isinstance(action, six.string_types):
                    action = str(action)
            else:
                action = '-->'

            options = []
            if bind:
                options.append('bound')
            if skip_if_none:
                options.append('skip if None')
            options = ', '.join(options)

            for idx in range(row_count):
                from_field = from_fields[idx]
                to_field = to_fields[idx]
                if to_list:
                    to_field = '[{}]'.format(to_field)
                if idx == 0:
                    data.append([from_field, action, to_field, options])
                else:
                    data.append([from_field, '+->', to_field, options])

        self.print(tables.format_pretty_table(data, column_names))
