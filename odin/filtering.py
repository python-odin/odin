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


class Filter(object):
    """
    Filtering util.
    """
    def __init__(self, *filters):
        self._filters = [(TraversalPath.parse(f), t, c) for f, t, c in filters]

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
