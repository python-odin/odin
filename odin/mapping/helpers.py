# -*- coding: utf-8 -*-


sum_fields = lambda *field_values: sum(field_values)


class cat_fields(object):
    """
    Helper for combining multiple fields
    """
    __slots__ = ('sep',)

    def __init__(self, sep=''):
        self.sep = sep

    def __call__(self, *field_values):
        return self.sep.join(field_values)


class split_field(object):
    """
    Helper for splitting a field into multiple fields.
    """
    __slots__ = ('sep', 'max_split',)

    def __init__(self, sep=None, max_split=None):
        self.sep = sep
        self.max_split = max_split

    def __call__(self, field_value):
        if self.max_split is None:
            return field_value.split(self.sep)
        else:
            return field_value.split(self.sep, self.max_split)
