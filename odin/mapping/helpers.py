# -*- coding: utf-8 -*-

sum_fields = lambda *field_values: sum(field_values)


class CatFields(object):
    """
    Helper for combining multiple fields
    """
    __slots__ = ('sep',)

    def __init__(self, sep=''):
        self.sep = sep

    def __call__(self, *field_values):
        return self.sep.join(field_values)

cat_fields = CatFields


class SplitField(object):
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

split_field = SplitField


class MapListOf(object):
    """
    Helper for mapping a ListOf field.

    This helper should be used along with the bind flag so the context object can be maintained.
    """
    __slots__ = ('mapping',)

    def __init__(self, mapping):
        self.mapping = mapping

    def __call__(self, bound_self, field_value):
        if field_value is None:
            return
        for f in field_value:
            yield self.mapping(f, context=bound_self.context).convert()


class MapDictAs(object):
    """
    Helper for mapping a DictAs field.

    This helper should be used along with the bind flag so the context object can be maintained.
    """
    __slots__ = ('mapping',)

    def __init__(self, mapping):
        self.mapping = mapping

    def __call__(self, bound_self, field_value):
        if field_value is None:
            return
        return self.mapping(field_value, context=bound_self.context).convert()
