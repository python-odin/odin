import pytest

from odin.mapping import helpers


class TestMappingHelpers:
    def test_sum_fields(self):
        actual = helpers.sum_fields(22, 20)

        assert actual == 42

    @pytest.mark.parametrize(
        "args, value, expected",
        (
            ((), ["ab", "cd"], "abcd"),
            (("-",), ["ab", "cd"], "ab-cd"),
        ),
    )
    def test_join_fields(self, args, value, expected):
        actual = helpers.join_fields(*args)(*value)

        assert actual == expected

    @pytest.mark.parametrize(
        "args, value, expected",
        (
            ((), "ab cd", ["ab", "cd"]),
            (("-",), "abcd", ["abcd"]),
            (("-",), "ab-cd", ["ab", "cd"]),
            (("-",), "ab-cd-ef", ["ab", "cd", "ef"]),
            (("-", 1), "ab-cd-ef", ["ab", "cd-ef"]),
        ),
    )
    def test_split_field(self, args, value, expected):
        actual = helpers.split_field(*args)(value)

        assert actual == expected
