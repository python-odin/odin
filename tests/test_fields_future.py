# -*- coding: utf-8 -*-
from __future__ import absolute_import

import enum
import pytest

from odin.exceptions import ValidationError
from odin.fields.future import EnumField


class Colour(enum.Enum):
    Red = "red"
    Green = "green"
    Blue = "blue"


class Options(enum.Enum):
    Undefined = ""
    Yes = "True"
    No = "False"


class Number(enum.IntEnum):
    Thirteen = 13
    FortyTwo = 42
    SixtyNine = 69


class TestEnumField(object):
    @pytest.mark.parametrize(
        ("field", "value", "actual"),
        (
            (EnumField(Colour), "red", Colour.Red),
            (EnumField(Colour), "green", Colour.Green),
            (EnumField(Colour), Colour.Blue, Colour.Blue),
            (EnumField(Colour, null=True), None, None),
            (EnumField(Colour, null=True), "", None),
            (EnumField(Options), "", Options.Undefined),
            (EnumField(Number), 13, Number.Thirteen),
            (EnumField(Number), 42, Number.FortyTwo),
            (EnumField(Number), Number.SixtyNine, Number.SixtyNine),
            (EnumField(Number, null=True), None, None),
        ),
    )
    def test_to_python__valid(self, field, value, actual):
        assert field.clean(value) == actual

    @pytest.mark.parametrize(
        ("field", "value"),
        (
            (EnumField(Colour), "pink"),
            (EnumField(Colour), True),
            (EnumField(Colour), None),
            (EnumField(Colour), ""),
            (EnumField(Colour), Number.Thirteen),
            (EnumField(Number), "13"),
            (EnumField(Number), 14),
            (EnumField(Number), None),
        ),
    )
    def test_to_python__invalid(self, field, value):
        with pytest.raises(ValidationError):
            field.clean(value)

    @pytest.mark.parametrize(
        "field, value, actual",
        (
            (EnumField(Colour), "red", None),
            (EnumField(Colour), Colour.Blue, "blue"),
            (EnumField(Colour), None, None),
            (EnumField(Number), 13, None),
            (EnumField(Number), Number.FortyTwo, 42),
            (EnumField(Number), None, None),
        ),
    )
    def test_prepare(self, field, value, actual):
        assert field.prepare(value) == actual

    @pytest.mark.parametrize(
        "field, expected",
        (
            (
                EnumField(Colour),
                ((Colour.Red, "Red"), (Colour.Green, "Green"), (Colour.Blue, "Blue")),
            ),
            (
                EnumField(Number),
                (
                    (Number.Thirteen, "Thirteen"),
                    (Number.FortyTwo, "FortyTwo"),
                    (Number.SixtyNine, "SixtyNine"),
                ),
            ),
            (
                EnumField(Colour, choices=(Colour.Red, Colour.Blue)),
                ((Colour.Red, "Red"), (Colour.Blue, "Blue")),
            ),
        ),
    )
    @pytest.mark.skipif("sys.version_info.major < 3")
    def test_choices(self, field, expected):
        assert field.choices == expected

    @pytest.mark.parametrize(
        "field, expected",
        (
            (
                EnumField(Colour),
                {(Colour.Red, "Red"), (Colour.Green, "Green"), (Colour.Blue, "Blue")},
            ),
            (
                EnumField(Number),
                {
                    (Number.Thirteen, "Thirteen"),
                    (Number.FortyTwo, "FortyTwo"),
                    (Number.SixtyNine, "SixtyNine"),
                },
            ),
            (
                EnumField(Colour, choices=(Colour.Red, Colour.Blue)),
                {(Colour.Red, "Red"), (Colour.Blue, "Blue")},
            ),
        ),
    )
    def test_choices__with_set(self, field, expected):
        """Use sets to handle random ordering in earlier Python releases"""
        assert set(field.choices) == expected

    @pytest.mark.parametrize(
        "field, expected",
        (
            (EnumField(Colour), (("red", "Red"), ("green", "Green"), ("blue", "Blue"))),
            (EnumField(Number), ((13, "Thirteen"), (42, "FortyTwo"), (69, "SixtyNine"))),
            (
                EnumField(Colour, choices=(Colour.Red, Colour.Blue)),
                (("red", "Red"), ("blue", "Blue")),
            ),
        ),
    )
    @pytest.mark.skipif("sys.version_info.major < 3")
    def test_choices_doc_text(self, field, expected):
        assert field.choices_doc_text == expected

    @pytest.mark.parametrize(
        "field, expected",
        (
            (EnumField(Colour), {("red", "Red"), ("green", "Green"), ("blue", "Blue")}),
            (EnumField(Number), {(13, "Thirteen"), (42, "FortyTwo"), (69, "SixtyNine")}),
            (
                EnumField(Colour, choices=(Colour.Red, Colour.Blue)),
                {("red", "Red"), ("blue", "Blue")},
            ),
        ),
    )
    def test_choices_doc_text__with_sets(self, field, expected):
        """Use sets to handle random ordering in earlier Python releases"""
        assert set(field.choices_doc_text) == expected
