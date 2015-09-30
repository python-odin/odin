# -*- coding: utf-8 -*-
from .traversal import TraversalPath


class Operator(object):
    """
    Operator to use in filtering
    """
    def __call__(self, value):
        raise NotImplementedError()


class Not(Operator):
    """
    Invert value of operator (this can be chained with other operators)
    """
    def __init__(self, expression):
        self.expression = expression

    def __call__(self, value):
        return not self.expression(value)


class Lambda(Operator):
    """
    Use a lambda expression as a filter.

    Lambda should except accept a single value and return a boolean indicating success/fail.
    """
    def __init__(self, expression):
        self.expression = expression

    def __call__(self, value):
        return self.expression(value)


class ComparisonOperator(Operator):
    def __init__(self, value):
        self.value = value

    def __call__(self, value):
        raise NotImplementedError()


class Eq(ComparisonOperator):
    def __call__(self, value):
        return value == self.value


class LT(ComparisonOperator):
    def __call__(self, value):
        return value < self.value


class LTE(ComparisonOperator):
    def __call__(self, value):
        return value <= self.value


class GT(ComparisonOperator):
    def __call__(self, value):
        return value > self.value


class GTE(ComparisonOperator):
    def __call__(self, value):
        return value >= self.value


class In(ComparisonOperator):
    def __call__(self, value):
        return value in self.value


class Is(ComparisonOperator):
    def __call__(self, value):
        return value is self.value


OPERATOR_MAP = {
    'eq': Eq,
    'lt': LT,
    'lte': LTE,
    'gt': GT,
    'gte': GTE,
    'in': In,
    'is': Is,
}


def parse_operator(operator):
    if operator is None:
        return
    if callable(operator):
        return operator
    # if isinstance(operator, six.string_types):
    #     result = None
    #     operator = operator.strip()
    #     invert = operator.startswith('!')
    raise ValueError("Invalid operator")


class Filter(object):
    """
    Filtering util.

    A filter entry is defined as a tuple containing three values (path, transform, check_operator).

    The *path* is a valid :py:class:`odin.traversal.TraversalPath` or a string that represents one.
    The *transform* is a callable that accepts a single argument and returns a value, an example could be
     :py:func:`len` to measure the length of a string or list; providing *None* will disable the transform.
    The *check_operator* is used to determine if the filter passes, the check operator is a callable that accepts a
     single value and returns a boolean indicating the outcome; providing *None* will test the value found at the
     provided path with the :py:func:`bool` function to determine if the filter passes. Using none makes sense for tests
     on a boolean field.

    """
    def __init__(self, *filters):
        self._filters = [(TraversalPath.parse(f), t, parse_operator(c)) for f, t, c in filters]

    def __and__(self, other):
        if isinstance(other, Filter):
            self._filters += other._filters
        raise ValueError('Other is not a Filter')

    def matches(self, resource):
        for field, transform, check in self._filters:
            try:
                value = field.get_value(resource)
            except (KeyError, IndexError):
                return False
            if transform:
                value = transform(value)
            if not(check(value) if check else value):
                return False
        return True
