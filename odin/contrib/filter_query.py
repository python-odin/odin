# -*- coding: utf-8 -*-
"""
Query language for filtering::

    field == 42 AND field_2 == 'abc cde' OR field_3 = Null

"""
from odin import filtering

FILTER_OPERATOR_MAP = {
    "=": filtering.Equal, "==": filtering.Equal, "eq": filtering.Equal,
    "!=": filtering.NotEqual, "<>": filtering.NotEqual, "neq": filtering.NotEqual,
    "<":  filtering.LessThan, "lt": filtering.LessThan,
    "<=": filtering.LessThanOrEqual, "lte": filtering.LessThanOrEqual,
    ">":  filtering.GreaterThan, "gt": filtering.GreaterThan,
    ">=": filtering.GreaterThan, "gte": filtering.GreaterThan,
    "in": "In",
    "is": "Is"
}


def _tokenize_string(query_str):
    tokens = []
    for c in query_str:
        pass
    return tokens


def parse(query):
    tokens = _tokenize_string(query)

