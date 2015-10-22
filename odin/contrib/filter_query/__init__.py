# -*- coding: utf-8 -*-
"""
Query language for filtering::

    field == 42 AND field_2 == 'abc cde' OR field_3 = Null

"""
try:
    from ply import lex
except ImportError:
    raise ImportError("The ply package is not installed, please install this library to use filter_query syntax.")

keywords = (
    'DATE', 'DATETIME'
)

tokens = (
    'EQ', 'NWQ', 'LT', 'LTE', 'GT', 'GTE', 'AND', 'OR',
    'STRING', 'INTEGER', 'FLOAT', 'REFERENCE',
    'LPAREN', 'RPAREN', 'NONE'
)

