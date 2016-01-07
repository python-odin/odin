def resource_reference(resource):
    return "{} <{}.{}>".format(resource._meta.resource_name, resource.__module__, resource.__name__)


def max_line_length(value):
    """
    Calculate maximum length of a line in a multi line string
    """
    return max(len(l) for l in value.split('\n'))


class Table(object):
    def __init__(self, columns=None):
        self._columns = columns
        self._rows = []
        self._header = None
        self._max_lengths = {}

    def _calculate_lengths(self, row):
        max_lengths = self._max_lengths
        for col, value in row.items():
            length = max_line_length(value)
            if length > max_lengths.setdefault(col, 0):
                max_lengths[col] = length

    def add_header(self, **kwargs):
        self._header = kwargs
        self._calculate_lengths(kwargs)
        if not self._columns:
            self._columns = self._header.keys()

    def add_row(self, **kwargs):
        self._rows.append(kwargs)
        self._calculate_lengths(kwargs)

    def _render_row(self, row, out, padding=' ', sep='|'):
        cols = []
        max_lengths = self._max_lengths
        for col in self._columns:
            value = row.get(col, '')
            cols.append('{}{}{}'.format(padding, value, padding * (max_lengths.get(col, 0) - len(value) + 1)))
        print('|', sep.join(cols), '|', sep='', file=out)

    def _render_separator(self, out, sep='-'):
        self._render_row({c: '' for c in self._columns}, out, padding=sep)

    def render(self, out):
        if self._header:
            self._render_row(self._header, out)
            self._render_separator(out, sep='=')
        else:
            self._render_separator(out)

        for row in self._rows:
            self._render_row(row, out)

        self._render_separator(out)
