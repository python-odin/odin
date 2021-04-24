# -*- coding: utf-8 -*-


def sum_fields(*field_values):
    """
    Return a sum of fields

    :param field_values:
    :return:

    """
    return sum(field_values)


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


class ApplyMapping(object):
    """
    Helper for applying a mapper.

    This helper should be used along with the bind flag so the context object can be maintained.
    """
    def __init__(self, mapping, allow_subclass=False):
        self.mapping = mapping
        self.allow_subclass = allow_subclass

    def __call__(self, bound_self, field_value):
        # Note this returns a tuple, this is expected
        return self.mapping.apply(field_value, context=bound_self.context, allow_subclass=self.allow_subclass),

    def __repr__(self):
        return "<%s: %s.%s>" % (self.__class__.__name__, self.mapping.__module__, self.mapping.__name__)

MapDictAs = MapListOf = ApplyMapping


class NoOpMapper(object):
    """
    Helper that provides the mapper interface performs no operation on the object.

    This is used with the MapListOf and MapDictAs fields when both contain the same Resource type.
    """
    @staticmethod
    def apply(source_obj, **_):
        return source_obj
