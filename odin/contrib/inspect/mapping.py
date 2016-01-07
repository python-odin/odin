import six

from .base import SummaryBase
from .utils import resource_reference, Table


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
        self.print()

        self.print("From:", resource_reference(mapping.from_obj))
        self.print("To:  ", resource_reference(mapping.to_obj))
        self.print()

        # Build mapping summary
        table = Table(['from_field', 'action', 'to_field'])
        table.add_header(from_field='From', action='Action', to_field='To')
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

            for idx in range(row_count):
                from_field = from_fields[idx]
                to_field = to_fields[idx]
                if to_list:
                    to_field = '[{}]'.format(to_field)
                if idx == 0:
                    table.add_row(from_field=from_field, action=action, to_field=to_field)
                else:
                    table.add_row(from_field=from_field, action='+->', to_field=to_field)

        table.render(self.out)