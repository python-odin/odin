def sum_fields(*field_values):
    """Return the sum of a number of fields.

    Example::

        define(from_field=("field_a", "field_b"), action=sum_fields, to_field="field_total")

    """
    return sum(field_values)


class JoinFields:
    """Helper for combining multiple fields.

    Example::

        define(from_field=("field_a", "field_b"), action=JoinFields(sep=":"), to_field="field_joined")

    """

    __slots__ = ("sep",)

    def __init__(self, sep: str = ""):
        self.sep = sep

    def __call__(self, *field_values) -> str:
        return self.sep.join(field_values)


join_fields = JoinFields
# Backwards compatibility
cat_fields = CatFields = JoinFields


class SplitField:
    """Helper for splitting a field into multiple fields.

    Example::

        define(from_field="field_joined", action=SplitField(sep=":"), to_field=("field_a", "field_b"))

    """

    __slots__ = (
        "sep",
        "max_split",
    )

    def __init__(self, sep: str = None, max_split: int = None):
        self.sep = sep
        self.max_split = max_split

    def __call__(self, field_value):
        if self.max_split is None:
            return field_value.split(self.sep)
        else:
            return field_value.split(self.sep, self.max_split)


split_field = SplitField


class ApplyMapping:
    """Helper for applying a mapper.

    This helper should be used along with the bind flag so the context object can be maintained.

    """

    def __init__(self, mapping, allow_subclass: bool = False):
        self.mapping = mapping
        self.allow_subclass = allow_subclass

    def __call__(self, bound_self, field_value):
        # Note this returns a tuple, this is expected
        return (
            self.mapping.apply(
                field_value,
                context=bound_self.context,
                allow_subclass=self.allow_subclass,
            ),
        )

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.mapping.__module__}.{self.mapping.__name__}>"


MapDictAs = MapListOf = ApplyMapping


class NoOpMapper:
    """Helper that provides the mapper interface performs no operation on the object.

    This is used with the MapListOf and MapDictAs fields when both contain the same Resource type.
    """

    @staticmethod
    def apply(source_obj, **_):
        return source_obj
