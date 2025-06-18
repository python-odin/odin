import sys
from typing import Annotated, Any, Dict, Final, List, Optional, Union

import pytest

import odin
from odin.annotated_resource import type_resolution

from ..resources_annotated import Book, From


class NonsenseField(odin.Field):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        raise TypeError("Nonsense!")

    def to_python(self, value):
        pass


class TestOptions:
    def test_kwargs__where_default_is_provided(self):
        target = type_resolution.Options(234, field_type=odin.StringField, my_value=123)

        actual = target._kwargs()

        assert actual == {
            "choices": None,
            "default": 234,
            "doc_text": "",
            "error_messages": None,
            "is_attribute": False,
            "key": False,
            "name": None,
            "use_default_if_not_provided": True,
            "validators": [],
            "verbose_name": None,
            "verbose_name_plural": None,
            "my_value": 123,
        }

    def test_kwargs__where_field_type_is_field_subclass(self):
        target = type_resolution.Options(field_type=odin.StringField, my_value=123)

        actual = target._kwargs()

        assert actual == {
            "choices": None,
            "doc_text": "",
            "error_messages": None,
            "is_attribute": False,
            "key": False,
            "name": None,
            "use_default_if_not_provided": True,
            "validators": [],
            "verbose_name": None,
            "verbose_name_plural": None,
            "my_value": 123,
        }

    def test_kwargs__where_field_type_is_not_field_subclass(self):
        target = type_resolution.Options(field_type=odin.ConstantField, my_value=123)

        actual = target._kwargs()

        assert actual == {
            "doc_text": "",
            "is_attribute": False,
            "key": False,
            "name": None,
            "verbose_name": None,
            "verbose_name_plural": None,
            "my_value": 123,
        }

    def test_init_field__where_field_is_defined(self):
        target = type_resolution.Options(field_type=odin.StringField)

        actual = target.construct_field()

        assert isinstance(actual, odin.StringField)

    def test_init_field__where_field_is_not_defined(self):
        target = type_resolution.Options()

        with pytest.raises(
            odin.exceptions.ResourceDefError,
            match="Field type `None` could not be resolved",
        ):
            target.construct_field()

    @pytest.mark.skipif(
        sys.version_info < (3, 10), reason="requires python3.10 or higher"
    )
    def test_init_field__where_field_has_invalid_args(self):
        target = type_resolution.Options(
            field_type=odin.StringField, my_invalid_arg="boom!"
        )

        with pytest.raises(
            odin.exceptions.ResourceDefError,
            match=r"StringField\.__init__\(\) got an unexpected keyword argument 'my_invalid_arg'",
        ):
            target.construct_field()

    @pytest.mark.skipif(
        sys.version_info < (3, 10), reason="requires python3.10 or higher"
    )
    def test_init_field__where_virtual_field_has_invalid_args(self):
        target = type_resolution.Options(
            field_type=odin.ConstantField, value="foo", my_invalid_arg="boom!"
        )

        with pytest.raises(
            odin.exceptions.ResourceDefError,
            match=r"ConstantField\.__init__\(\) got an unexpected keyword argument 'my_invalid_arg'",
        ):
            target.construct_field()

    @pytest.mark.skipif(
        sys.version_info < (3, 10), reason="requires python3.10 or higher"
    )
    def test_init_field__where_field_has_missing_required_arg(self):
        target = type_resolution.Options(field_type=odin.EnumField)

        with pytest.raises(
            odin.exceptions.ResourceDefError,
            match=r"EnumField\.__init__\(\) missing 1 required positional argument: 'enum_type'",
        ):
            target.construct_field()

    def test_init_field__where_unknown_type_error_raised(self):
        target = type_resolution.Options(field_type=NonsenseField)

        with pytest.raises(TypeError, match=r"Nonsense!"):
            target.construct_field()


class TestAnyField:
    @pytest.mark.parametrize(
        "target, value, expected",
        (
            (type_resolution.AnyField(), None, None),
            (type_resolution.AnyField(), "abc", "abc"),
            (type_resolution.AnyField(), 123, 123),
        ),
    )
    def test_to_python(self, target, value, expected):
        actual = target.to_python(value)

        assert actual == expected


@pytest.mark.parametrize(
    "tp, value, expected_field_type, expected_default",
    [
        (str, odin.NotProvided, odin.StringField, odin.NotProvided),
        (str, "foo", odin.StringField, "foo"),
        # Defined as a field
        (int, odin.IntegerField(default=123), odin.IntegerField, 123),
        # Defined with Options
        (str, odin.Options("bar"), odin.StringField, "bar"),
        # Explicit type provided to options
        (
            str,
            odin.Options(field_type=odin.IntegerField),
            odin.IntegerField,
            odin.NotProvided,
        ),
        (odin.types.IPv46, odin.NotProvided, odin.IPv46Field, odin.NotProvided),
        (odin.types.Url | None, odin.NotProvided, odin.UrlField, odin.NotProvided),
        (From, odin.NotProvided, odin.EnumField, odin.NotProvided),
        (Optional[From], odin.NotProvided, odin.EnumField, odin.NotProvided),
        (Book | None, odin.NotProvided, odin.DictAs, odin.NotProvided),
        # List types
        (List, odin.NotProvided, odin.ListField, list),
        (list, odin.NotProvided, odin.ListField, list),
        (List[Book], odin.NotProvided, odin.ListOf, list),
        (list[Book], odin.NotProvided, odin.ListOf, list),
        # Dict types
        (Dict, odin.NotProvided, odin.DictField, dict),
        (Dict[str, Book], odin.NotProvided, odin.DictOf, dict),
        # Types using annotation
        (
            Annotated[str, odin.Options(verbose_name="Foo")],
            odin.NotProvided,
            odin.StringField,
            odin.NotProvided,
        ),
        (
            Annotated[str, odin.Options(verbose_name="Foo")],
            "foo",
            odin.StringField,
            "foo",
        ),
        (
            Annotated[int, str],
            42,
            odin.IntegerField,
            42,
        ),
        (
            Annotated[int | None, odin.Options()],
            42,
            odin.IntegerField,
            42,
        ),
    ],
)
def test_process_attribute__where_type_is_supported(
    tp, value, expected_field_type, expected_default
):
    actual = type_resolution.process_attribute(tp, value)

    assert isinstance(actual, expected_field_type)
    assert actual.default == expected_default


def test_process_attribute__where_is_a_resource():
    actual = type_resolution.process_attribute(Book, odin.NotProvided)

    assert isinstance(actual, odin.DictAs)
    assert actual.default is Book


def test_process_attribute__where_type_is_constant():
    actual = type_resolution.process_attribute(Final[str], "my-constant")

    assert isinstance(actual, odin.ConstantField)
    assert actual.value == "my-constant"


def test_process_attribute__where_constant_missing_value():
    with pytest.raises(
        odin.exceptions.ResourceDefError, match="Final fields require a value"
    ):
        type_resolution.process_attribute(Final[str], odin.NotProvided)


@pytest.mark.parametrize(
    "tp, expected_field_type",
    [
        (Optional[str], odin.StringField),
        (None | int, odin.IntegerField),
        (float | None, odin.FloatField),
        (Union[int, None], odin.IntegerField),
        (list[str] | None, odin.TypedListField),
    ],
)
def test_process_attribute__where_nullable_type(tp, expected_field_type):
    actual = type_resolution.process_attribute(tp, odin.NotProvided)

    assert isinstance(actual, expected_field_type)
    assert actual.null


@pytest.mark.parametrize(
    "tp, expected_sub_field_type",
    [
        (list[str], odin.StringField),
        (list[int | None], odin.IntegerField),
        (list[From], odin.EnumField),
        (list[Any], type_resolution.AnyField),
        (List[str], odin.StringField),
        (list[Annotated[str, odin.Options(verbose_name="Foo")]], odin.StringField),
    ],
)
def test_process_attribute__where_typed_list(tp, expected_sub_field_type):
    actual = type_resolution.process_attribute(tp, odin.NotProvided)

    assert isinstance(actual, odin.TypedListField)
    assert isinstance(actual.field, expected_sub_field_type)


@pytest.mark.parametrize(
    "tp, expected_key_field_type, expected_value_field_type",
    [
        (dict[str, str], odin.StringField, odin.StringField),
        (dict[int, str | None], odin.IntegerField, odin.StringField),
        (Dict[str, str], odin.StringField, odin.StringField),
        (Dict[int, str | None], odin.IntegerField, odin.StringField),
    ],
)
def test_process_attribute__where_typed_dict(
    tp, expected_key_field_type, expected_value_field_type
):
    actual = type_resolution.process_attribute(tp, odin.NotProvided)

    assert isinstance(actual, odin.TypedDictField)
    assert isinstance(actual.key_field, expected_key_field_type)
    assert isinstance(actual.value_field, expected_value_field_type)


@pytest.mark.parametrize(
    "tp, value, expected_error",
    [
        (object, None, "Unable to resolve field for type <class 'object'>"),
        (
            Union[str, int],
            None,
            "Union type are only supported with a single type and None",
        ),
        ("my-type", None, "Annotation is not a type instance 'my-type'"),
        (
            Union[str, int],
            None,
            "Union type are only supported with a single type and None",
        ),
        (
            Union[str, None, int],
            None,
            "Union type are only supported with a single type and None",
        ),
        (
            Annotated[str, int],
            odin.Options(),
            "Options should included in the Annotation",
        ),
    ],
)
def test_process_attribute__where_type_is_not_supported(tp, value, expected_error):
    with pytest.raises(type_resolution.ResourceDefError, match=expected_error):
        type_resolution.process_attribute(tp, value)


# @pytest.mark.parametrize(
#     "type_, expected_key_field, expected_value_field",
#     (
#         (
#             Dict[str, str],
#             odin.StringField,
#             odin.StringField,
#         ),
#         (
#             Dict[str, From],
#             odin.StringField,
#             odin.EnumField,
#         ),
#         (
#             Dict[str, Any],
#             odin.StringField,
#             AnyField,
#         ),
#     ),
# )
# def test_resolve_field_from_sub_scripted_type__where_field_can_be_resolved_to_typed_dict(
#     type_, expected_key_field, expected_value_field
# ):
#     options = type_resolution.Options()
#     origin = type_resolution.get_origin(type_)
#
#     type_resolution._resolve_field_from_sub_scripted_type(origin, options, type_)
#
#     assert options.field_type is odin.TypedDictField
#     assert isinstance(options.field_args["key_field"], expected_key_field)
#     assert isinstance(options.field_args["value_field"], expected_value_field)
