# -*- coding: utf-8 -*-
import six
from .exceptions import InvalidPathError
from .traversal import TraversalPath


class FilterAtom(object):
    """
    Base filter statement
    """
    def __name__(self):
        return self.__class__.__name__

    def __call__(self, resource):
        raise NotImplementedError()

    def any(self, collection):
        return any(self(r) for r in collection)

    def all(self, collection):
        return all(self(r) for r in collection)


class FilterChain(FilterAtom):
    operator_name = ''
    check_operator = all

    def __init__(self, *atoms):
        self._atoms = list(atoms)

    def __len__(self):
        return len(self._atoms)

    def __add__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(*self._atoms + other._atoms)
        elif isinstance(other, FilterComparison):
            self._atoms.append(other)
            return self
        raise TypeError("{0} not supported for this operation".format(other))

    def __call__(self, resource):
        return self.check_operator(a(resource) for a in self._atoms)

    def __str__(self):
        if not self._atoms:
            return ''
        pin = " {0} ".format(self.operator_name)
        return "({0})".format(pin.join(str(a) for a in self._atoms))


class And(FilterChain):
    operator_name = 'AND'
    check_operator = all


class Or(FilterChain):
    operator_name = 'OR'
    check_operator = any


class FilterComparison(FilterAtom):
    """
    Base class for filter operator atoms
    """
    # Symbol for this operator and alternatives. The first item is used when generating
    # a representation of the filter, the others are used for parsing queries.
    operator_symbols = []

    def __init__(self, field, value, operation=None):
        self.field = TraversalPath.parse(field)
        self.value = value
        self.operation = operation

    def __call__(self, resource):
        try:
            value = self.field.get_value(resource)
        except InvalidPathError:
            return False
        else:
            if self.operation:
                value = self.operation(value)
            return self.compare(value)

    def __str__(self):
        value = self.value
        if isinstance(self.value, six.string_types):
            value = "'{0}'".format(value)

        if self.operation:
            op_name = getattr(self.operation, 'name', self.operation.__name__)
            return "{0}({1}) {2} {3}".format(op_name, self.field, self.operator_symbols[0], value)
        else:
            return "{0} {1} {2}".format(self.field, self.operator_symbols[0], value)

    def compare(self, value):
        raise NotImplementedError()


class Equal(FilterComparison):
    operator_symbols = ('==', '=', 'eq')

    def compare(self, value):
        return value == self.value


class NotEqual(FilterComparison):
    operator_symbols = ('!=', '<>', 'neq')

    def compare(self, value):
        return value != self.value


class LessThan(FilterComparison):
    operator_symbols = ('<', 'lt')

    def compare(self, value):
        return value < self.value


class LessThanOrEqual(FilterComparison):
    operator_symbols = ('<=', 'lte')

    def compare(self, value):
        return value <= self.value


class GreaterThan(FilterComparison):
    operator_symbols = ('>', 'gt')

    def compare(self, value):
        return value > self.value


class GreaterThanOrEqual(FilterComparison):
    operator_symbols = ('>=', 'gte')

    def compare(self, value):
        return value >= self.value
