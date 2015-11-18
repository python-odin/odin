# -*- coding: utf-8 -*-
"""
Query language for filtering::

    field == 42 AND field_2 == 'abc cde' OR field_3 = Null

"""
from ply import lex
from odin import filtering

tokens = (
    'STRING', 'INTEGER', 'FLOAT',
    'EQ', 'NEQ', 'LT', 'LTE', "GT", "GTE",
    'LPAREN', 'RPAREN', ''
)

t_STRING = r'\".+\"'


def t_INTEGER(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_FLOAT(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t




FILTER_OPERATOR_MAP = {
    "=": filtering.Equal, "==": filtering.Equal, "eq": filtering.Equal,
    "!=": filtering.NotEqual, "<>": filtering.NotEqual, "neq": filtering.NotEqual,
    "<":  filtering.LessThan, "lt": filtering.LessThan,
    "<=": filtering.LessThanOrEqual, "lte": filtering.LessThanOrEqual,
    ">":  filtering.GreaterThan, "gt": filtering.GreaterThan,
    ">=": filtering.GreaterThanOrEqual, "gte": filtering.GreaterThanOrEqual,
    "in": "In",
    "is": "Is"
}


def _tokenize_string(query_str):
    tokens = []
    in_string = False
    for c in query_str:
        if c == ' ':
            pass
    return tokens


def parse(query):
    tokens = _tokenize_string(query)
