import pytest

from odin import utils
from odin.utils import getmeta

from .resources import Book


class TestCamelAndDashFormats:
    def test_camel_to_lower_separated(self):
        assert "this_is_an_example" == utils.camel_to_lower_underscore(
            "thisIsAnExample"
        )
        assert "this_is_an_example" == utils.camel_to_lower_underscore(
            "ThisIsAnExample"
        )
        assert "this-is-a-test" == utils.camel_to_lower_dash("thisIsATest")

    def test_lower_underscore_to_camel(self):
        assert "thisIsAnExample" == utils.lower_underscore_to_camel(
            "this_is_an_example"
        )
        assert "thisIsAnExample" == utils.lower_underscore_to_camel(
            "this_is_an_example"
        )
        assert "thisIsATest" == utils.lower_underscore_to_camel("this_Is_A_test")

    def test_lower_dash_to_camel(self):
        assert "thisIsAnExample" == utils.lower_dash_to_camel("this-is-an-example")
        assert "thisIsAnExample" == utils.lower_dash_to_camel("this-is-an-example")
        assert "thisIsATest" == utils.lower_dash_to_camel("this-Is-A-test")


class TestIterator:
    def test_extract_fields_from_dict(self):
        source_dict = {
            "title": "My Title",
            "num_pages": 1,
            "rrp": 1.2,
            "fiction": True,
            "published": ["no_validation_for_type"],
            "another_field": "that is not on the resource",
        }

        assert {
            "title": "My Title",
            "num_pages": 1,
            "rrp": 1.2,
            "fiction": True,
            "published": ["no_validation_for_type"],
        } == utils.extract_fields_from_dict(source_dict, Book)


class TestFilterFields:
    @pytest.fixture
    def field_map(self):
        return getmeta(Book).field_map

    @pytest.mark.parametrize(
        "kwargs, expected_fields, expected_readonly",
        (
            (
                {},
                {
                    "title",
                    "isbn",
                    "num_pages",
                    "rrp",
                    "fiction",
                    "genre",
                    "published",
                    "authors",
                    "publisher",
                },
                set(),
            ),
            ({"include": ["title", "isbn"]}, {"title", "isbn"}, set()),
            (
                {"exclude": ["rrp", "fiction", "genre", "publisher", "authors"]},
                {"title", "isbn", "num_pages", "published"},
                set(),
            ),
            (
                {
                    "include": ["title", "isbn"],
                    "exclude": ["isbn", "rrp", "fiction", "genre"],
                },
                {"title"},
                set(),
            ),
            (
                {"include": ["title", "isbn"], "readonly": ["isbn"]},
                {"title", "isbn"},
                {"isbn"},
            ),
            (
                {"include": ["title", "isbn"], "readonly": ["isbn", "rrp"]},
                {"title", "isbn"},
                {"isbn"},
            ),
            (
                {
                    "include": ["title", "isbn", "rrp"],
                    "exclude": ["rrp"],
                    "readonly": ["isbn", "rrp"],
                },
                {"title", "isbn"},
                {"isbn"},
            ),
        ),
    )
    def test_filtering(self, field_map, kwargs, expected_fields, expected_readonly):
        fields, readonly = utils.filter_fields(field_map, **kwargs)

        assert fields == expected_fields
        assert readonly == expected_readonly


class TestValueInChoice:
    CHOICES = (
        ("foo", "Foo"),
        ("bar", "Foo"),
        (123, "Number"),
        (True, "Boolean"),
        (None, "None"),
        ("eek", "With Help", "Help string"),
    )

    def test_value_in_choices(self):
        assert utils.value_in_choices("foo", self.CHOICES)
        assert utils.value_in_choices(123, self.CHOICES)
        assert utils.value_in_choices(True, self.CHOICES)
        assert utils.value_in_choices(None, self.CHOICES)
        assert utils.value_in_choices("eek", self.CHOICES)
        assert not utils.value_in_choices("xyz", self.CHOICES)
        assert not utils.value_in_choices(False, self.CHOICES)
        assert not utils.value_in_choices(321, self.CHOICES)


class TestForceTuple:
    """
    Tests for odin.utils.force_tuple
    """

    @pytest.mark.parametrize(
        ("value", "expected"),
        (
            (None, ()),
            ("", ("",)),
            (0, (0,)),
            (False, (False,)),
            (True, (True,)),
            (123, (123,)),
            ("Foo", ("Foo",)),
            (["Foo", "bar"], ("Foo", "bar")),
            (("Foo", "bar"), ("Foo", "bar")),
            (["Foo", 123, "bar", "eek"], ("Foo", 123, "bar", "eek")),
        ),
    )
    def test_values(self, value, expected):
        assert utils.force_tuple(value) == expected


class TestChunk:
    """
    Tests for odin.utils.chunk
    """

    @pytest.mark.parametrize(
        ("value", "size", "expected"),
        (
            (
                "This is a block of text split by 4",
                4,
                [
                    ["T", "h", "i", "s"],
                    [" ", "i", "s", " "],
                    ["a", " ", "b", "l"],
                    ["o", "c", "k", " "],
                    ["o", "f", " ", "t"],
                    ["e", "x", "t", " "],
                    ["s", "p", "l", "i"],
                    ["t", " ", "b", "y"],
                    [" ", "4"],
                ],
            ),
        ),
    )
    def test_small_values(self, value, size, expected):
        """Small scale test (eg small iterable that can be easily verified)"""
        assert [list(c) for c in utils.chunk(value, size)] == expected

    def test_empty_iterable(self):
        assert list(utils.chunk([], 3)) == []

    def test_generator_consumption(self):
        gen = (x for x in range(5))
        assert list(utils.chunk(gen, 2)) == [(0, 1), (2, 3), (4,)]

    def test_outer_generator_consumption_without_inner_exhaustion(self):
        """Ensure chunk does not infinite loop when outer generator is collected into a list."""
        chunks = list(utils.chunk("abcdef", 2))
        assert chunks == [("a", "b"), ("c", "d"), ("e", "f")]

    @pytest.mark.parametrize("size", (0, -1, -10))
    def test_invalid_size(self, size):
        with pytest.raises(ValueError, match="n must be at least 1"):
            list(utils.chunk([1, 2, 3], size))


class TestCachedProperty:
    """
    Tests for odin.utils.cached_property and clear_cached_properties
    """

    class TargetClass:
        def __init__(self, value):
            self.value = value
            self.calc_count = 0

        @utils.cached_property
        def computed(self):
            self.calc_count += 1
            return self.value * 2

    def test_cached_property_caches_value(self):
        obj = self.TargetClass(5)
        assert obj.calc_count == 0

        assert obj.computed == 10
        assert obj.calc_count == 1

        # Second access uses cache
        assert obj.computed == 10
        assert obj.calc_count == 1

    def test_clear_cached_properties(self):
        obj = self.TargetClass(5)
        assert obj.computed == 10
        assert obj.calc_count == 1

        obj.value = 7
        utils.clear_cached_properties(obj)

        # After clearing, computed is re-evaluated
        assert obj.computed == 14
        assert obj.calc_count == 2
