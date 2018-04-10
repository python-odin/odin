# -*- coding: utf-8 -*-
from __future__ import absolute_import

import pytest

from odin.exceptions import ValidationError

try:
    from odin.fields.future import EnumField
except ImportError:
    pass
else:
    import enum


    class Colour(enum.Enum):
        Red = 'red'
        Green = 'green'
        Blue = 'blue'


    class Number(enum.IntEnum):
        Thirteen = 13
        FortyTwo = 42
        SixtyNine = 69


    class TestEnumField(object):
        @pytest.mark.parametrize(('field', 'value', 'actual'), (
            (EnumField(Colour), 'red', Colour.Red),
            (EnumField(Colour), 'green', Colour.Green),
            (EnumField(Colour), Colour.Blue, Colour.Blue),
            (EnumField(Colour, null=True), None, None),
            (EnumField(Number), 13, Number.Thirteen),
            (EnumField(Number), 42, Number.FortyTwo),
            (EnumField(Number), Number.SixtyNine, Number.SixtyNine),
            (EnumField(Number, null=True), None, None),
        ))
        def test_to_python__valid(self, field, value, actual):
            assert field.clean(value) == actual

        @pytest.mark.parametrize(('field', 'value'), (
            (EnumField(Colour), 'pink'),
            (EnumField(Colour), True),
            (EnumField(Colour), None),
            (EnumField(Colour), Number.Thirteen),
            (EnumField(Number), '13'),
            (EnumField(Number), 14),
            (EnumField(Number), None),
        ))
        def test_to_python__invalid(self, field, value):
            with pytest.raises(ValidationError):
                field.clean(value)

        @pytest.mark.parametrize(('field', 'value', 'actual'), (
            (EnumField(Colour), 'red', None),
            (EnumField(Colour), Colour.Blue, 'blue'),
            (EnumField(Colour), None, None),
            (EnumField(Number), 13, None),
            (EnumField(Number), Number.FortyTwo, 42),
            (EnumField(Number), None, None),
        ))
        def test_prepare(self, field, value, actual):
            assert field.prepare(value) == actual
