# -*- coding: utf-8 -*-
import six
from .traversal import TraversalPath


class FilterAtom(object):
    """
    Base filter statement
    """
    def __call__(self, resource):
        raise NotImplementedError()

    def any(self, collection):
        return any(self(i) for i in collection)

    def all(self, collection):
        return all(self(i) for i in collection)


class And(FilterAtom):
    def __init__(self, *atoms):
        self._atoms = atoms

    def __add__(self, other):
        if isinstance(other, self.__class__):
            return And(self._atoms + other._atoms)
        elif isinstance(other, FilterComparison):
            self._atoms += other
            return self
        raise TypeError("{} not supported for this operation".format(other))

    def __call__(self, resource):
        return all(a(resource) for a in self._atoms)


class Or(FilterAtom):
    def __init__(self, *atoms):
        self._atoms = atoms

    def __add__(self, other):
        if isinstance(other, self.__class__):
            return Or(self._atoms + other._atoms)
        elif isinstance(other, FilterComparison):
            self._atoms += other
            return self
        raise TypeError("{} not supported for this operation".format(other))

    def __call__(self, resource):
        return any(a(resource) for a in self._atoms)


class FilterComparison(FilterAtom):
    """
    Base class for filter operator atoms
    """
    def __init__(self, field, value, operation=None):
        self.field = TraversalPath.parse(field)
        self.value = value
        self.operation = operation

    def __call__(self, resource):
        try:
            value = self.field.get_value(resource)
        except KeyError:
            return False
        else:
            if self.operation:
                value = self.operation(value)
            return self.compare(value)

    def compare(self, value):
        raise NotImplementedError()


class Equal(FilterComparison):
    def compare(self, value):
        return value == self.value


class NotEqual(FilterComparison):
    def compare(self, value):
        return value != self.value


class LessThan(FilterComparison):
    def compare(self, value):
        return value < self.value


class LessThanOrEqual(FilterComparison):
    def compare(self, value):
        return value <= self.value


class GreaterThan(FilterComparison):
    def compare(self, value):
        return value > self.value


class GreaterThanOrEqual(FilterComparison):
    def compare(self, value):
        return value >= self.value


FILTER_OPERATOR_MAP = {
    "=": Equal, "eq": Equal,
    "!=": NotEqual, "<>": NotEqual, "neq": NotEqual,
    "<": LessThan, "lt": LessThan,
    "<=": LessThanOrEqual, "lte": LessThanOrEqual,
    ">": GreaterThan, "gt": GreaterThan,
    ">=": GreaterThan, "gte": GreaterThan,
    "in": "In",
    "is": "Is"
}


TOKEN_SEPARATORS = ' \n'
START_GROUP = '('
END_GROUP = ')'
STRING_DELIMITERS = '"'


def split_atoms(expression):
    atoms = []
    start_idx = 0
    in_string = False
    for idx, c in enumerate(expression.strip(TOKEN_SEPARATORS)):
        if c in STRING_DELIMITERS:
            if in_string:
                pass


def parse_filter_expression(expression):
    current_atoms = atoms = []
