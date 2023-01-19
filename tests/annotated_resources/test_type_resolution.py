import sys
from typing import Optional, Union, List, Dict, Tuple, Any, Final

import pytest

import odin
from odin.annotated_resource import type_resolution
from odin.annotated_resource.special_fields import AnyField

from ..resources_annotated import From, Book


class NonsenseField(odin.Field):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        raise TypeError("Nonsense!")

    def to_python(self, value):
        pass


class TestOptions:
    def test_kwargs__where_field_type_is_field_subclass(self):
        target = type_resolution.Options(field_type=odin.StringField, my_value=123)

        actual = target._kwargs()

        assert actual == {
            "choices": None,
            "default": odin.fields.NotProvided,
            "doc_text": "",
            "error_messages": None,
            "is_attribute": False,
            "key": False,
            "name": None,
            "use_default_if_not_provided": True,
            "validators": None,
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

        actual = target.init_field()

        assert isinstance(actual, odin.StringField)

    def test_init_field__where_field_is_not_defined(self):
        target = type_resolution.Options()

        with pytest.raises(
            odin.exceptions.ResourceDefError,
            match="Field type `None` could not be resolved",
        ):
            target.init_field()

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
            target.init_field()

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
            target.init_field()

    @pytest.mark.skipif(
        sys.version_info < (3, 10), reason="requires python3.10 or higher"
    )
    def test_init_field__where_field_has_missing_required_arg(self):
        target = type_resolution.Options(field_type=odin.EnumField)

        with pytest.raises(
            odin.exceptions.ResourceDefError,
            match=r"EnumField\.__init__\(\) missing 1 required positional argument: 'enum_type'",
        ):
            target.init_field()

    def test_init_field__where_unknown_type_error_raised(self):
        target = type_resolution.Options(field_type=NonsenseField)

        with pytest.raises(TypeError, match=r"Nonsense!"):
            target.init_field()


@pytest.mark.parametrize(
    "type_, expected",
    (
        (str, odin.StringField),
        (odin.types.IPv46, odin.IPv46Field),
        (From, odin.EnumField),
        (Book, odin.DictAs),
    ),
)
def test_resolve_field_from_type__where_type_can_be_resolved(type_, expected):
    options = type_resolution.Options()

    type_resolution._resolve_field_from_type(options, type_)

    assert options.field_type is expected


def test_resolve_field_from_type__where_type_cannot_be_resolved():
    options = type_resolution.Options()

    with pytest.raises(
        odin.exceptions.ResourceDefError,
        match="Unable to resolve field for type <class 'object'>",
    ):
        type_resolution._resolve_field_from_type(options, object)


@pytest.mark.parametrize(
    "type_, expected",
    (
        (Optional[str], True),
        (Union[str, None], True),
        (Union[int, float], False),
        (Union[int, float, None], False),
    ),
)
def test_is_optional(type_, expected):
    actual = type_resolution.is_optional(type_)

    assert actual is expected


@pytest.mark.parametrize(
    "type_, expected",
    (
        (Optional[str], odin.StringField),
        (Union[str, None], odin.StringField),
        (List, odin.ListField),
        (List[Book], odin.ListOf),
        (Dict, odin.DictField),
        (Dict[str, Book], odin.DictOf),
    ),
)
def test_resolve_field_from_sub_scripted_type__where_field_can_be_resolved(
    type_, expected
):
    options = type_resolution.Options()
    origin = type_resolution.get_origin(type_)

    type_resolution._resolve_field_from_sub_scripted_type(origin, options, type_)

    assert options.field_type is expected


@pytest.mark.parametrize(
    "type_, expected_field",
    (
        (
            List[str],
            odin.StringField,
        ),
        (
            List[From],
            odin.EnumField,
        ),
        (
            List[Any],
            AnyField,
        ),
    ),
)
def test_resolve_field_from_sub_scripted_type__where_field_can_be_resolved_to_typed_list(
    type_, expected_field
):
    options = type_resolution.Options()
    origin = type_resolution.get_origin(type_)

    type_resolution._resolve_field_from_sub_scripted_type(origin, options, type_)

    assert options.field_type is odin.TypedListField
    assert isinstance(options.field_args["field"], expected_field)


@pytest.mark.parametrize(
    "type_, expected_key_field, expected_value_field",
    (
        (
            Dict[str, str],
            odin.StringField,
            odin.StringField,
        ),
        (
            Dict[str, From],
            odin.StringField,
            odin.EnumField,
        ),
        (
            Dict[str, Any],
            odin.StringField,
            AnyField,
        ),
    ),
)
def test_resolve_field_from_sub_scripted_type__where_field_can_be_resolved_to_typed_dict(
    type_, expected_key_field, expected_value_field
):
    options = type_resolution.Options()
    origin = type_resolution.get_origin(type_)

    type_resolution._resolve_field_from_sub_scripted_type(origin, options, type_)

    assert options.field_type is odin.TypedDictField
    assert isinstance(options.field_args["key_field"], expected_key_field)
    assert isinstance(options.field_args["value_field"], expected_value_field)


@pytest.mark.parametrize(
    "type_",
    (
        Union[int, float],
        Tuple[int, float],
        Tuple,
    ),
)
def test_resolve_field_from_sub_scripted_type__where_type_is_unsupported(type_):
    options = type_resolution.Options()
    origin = type_resolution.get_origin(type_)

    with pytest.raises(
        odin.exceptions.ResourceDefError,
        match="Unable to resolve field for sub-scripted type",
    ):
        type_resolution._resolve_field_from_sub_scripted_type(origin, options, type_)


@pytest.mark.parametrize(
    "type_, expected_type, expected_args",
    (
        # Basic types
        (str, odin.StringField, {}),
        (list, odin.ListField, {}),
        (dict, odin.DictField, {}),
        (odin.types.Email, odin.EmailField, {}),
        (Optional[odin.types.Url], odin.UrlField, {"null": True}),
        # List/Dict types
        (List[Book], odin.ListOf, {"resource": Book}),
        (Dict[str, Book], odin.DictOf, {"resource": Book}),
        # Enums
        (From, odin.EnumField, {"enum_type": From}),
        (Optional[From], odin.EnumField, {"enum_type": From, "null": True}),
    ),
)
def test_resolve_field_from_annotation__where_field_can_be_resolved(
    type_, expected_type, expected_args
):
    options = type_resolution.Options()

    type_resolution._resolve_field_from_annotation(options, type_)
    actual_args = options._kwargs()

    assert options.field_type is expected_type
    assert all(
        actual_args.get(key) == value for key, value in expected_args.items()
    ), f"Expected args {expected_args} not found in {actual_args}"


def test_resolve_field_from_annotation__for_list_field():
    options = type_resolution.Options()

    type_resolution._resolve_field_from_annotation(options, List[bool])
    actual_args = options._kwargs()

    assert options.field_type is odin.TypedListField
    assert actual_args["default"] is list
    assert isinstance(actual_args["field"], odin.BooleanField)


def test_resolve_field_from_annotation__for_dict_field():
    options = type_resolution.Options()

    type_resolution._resolve_field_from_annotation(options, Dict[str, int])
    actual_args = options._kwargs()

    assert options.field_type is odin.TypedDictField
    assert actual_args["default"] is dict
    assert isinstance(actual_args["key_field"], odin.StringField)
    assert isinstance(actual_args["value_field"], odin.IntegerField)


def test_resolve_field_from_annotation__for_nested_dict_types():
    options = type_resolution.Options()

    type_resolution._resolve_field_from_annotation(options, Dict[str, List[int]])
    actual_args = options._kwargs()

    assert options.field_type is odin.TypedDictField
    assert actual_args["default"] is dict
    assert isinstance(actual_args["key_field"], odin.StringField)
    assert isinstance(actual_args["value_field"], odin.TypedListField)
    # Nested field type
    assert isinstance(actual_args["value_field"].field, odin.IntegerField)


def test_resolve_field_from_annotation__not_a_type():
    options = type_resolution.Options()

    with pytest.raises(
        odin.exceptions.ResourceDefError, match="Annotation is not a type instance"
    ):
        type_resolution._resolve_field_from_annotation(options, object())


@pytest.mark.parametrize(
    "type_, value, expected_type, expected_default",
    (
        (str, odin.NotProvided, odin.StringField, odin.NotProvided),
        (str, "foo", odin.StringField, "foo"),
        # Defined as a field
        (str, odin.IntegerField(default=123), odin.IntegerField, 123),
        # Defined with Options
        (str, odin.Options("bar"), odin.StringField, "bar"),
        # Explicit type provided to options
        (
            str,
            odin.Options(field_type=odin.IntegerField),
            odin.IntegerField,
            odin.NotProvided,
        ),
    ),
)
def test_process_attribute__where_assumed_valid(
    type_, value, expected_type, expected_default
):
    actual = type_resolution.process_attribute(type_, value)

    assert isinstance(actual, expected_type)
    assert actual.default == expected_default


class TestSpecialFields:
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

    def test_constant_field__where_field_is_defined_correctly(self):
        actual = type_resolution.process_attribute(Final[str], "foo")

        assert isinstance(actual, odin.ConstantField)
        assert actual.value == "foo"

    def test_constant_field__where_value_is_missing(self):
        with pytest.raises(
            odin.exceptions.ResourceDefError, match="Final fields require a value"
        ):
            type_resolution.process_attribute(Final[str], odin.NotProvided)
