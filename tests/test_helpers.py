import pytest

from odin import helpers
from odin.exceptions import NON_FIELD_ERRORS, ValidationError
from odin.utils import getmeta

from .resources import Author, Book


class TestValidationErrorCollection:
    def test_bool__when_empty(self):
        # Arrange
        target = helpers.ValidationErrorCollection()

        # Act
        result = bool(target)

        # Assert
        assert result is False

    def test_bool__when_messages_present(self):
        # Arrange
        target = helpers.ValidationErrorCollection()
        target.add_message("name", "this is required")

        # Act
        result = bool(target)

        # Assert
        assert result is True

    def test_bool__when_empty_messages_added(self):
        # Arrange
        target = helpers.ValidationErrorCollection()
        target.add_message("name")

        # Act
        result = bool(target)

        # Assert
        assert result is False

    def test_len__when_empty(self):
        # Arrange
        target = helpers.ValidationErrorCollection()

        # Act
        result = len(target)

        # Assert
        assert result == 0

    def test_len__with_multiple_fields(self):
        # Arrange
        target = helpers.ValidationErrorCollection()
        target.add_message("name", "this is required")
        target.add_message("title", "too short")

        # Act
        result = len(target)

        # Assert
        assert result == 2

    def test_contains__with_string_field_name(self):
        # Arrange
        target = helpers.ValidationErrorCollection()
        target.add_message("name", "this is required")

        # Act & Assert
        assert "name" in target
        assert "title" not in target

    def test_contains__with_field_instance(self):
        # Arrange
        field_name = getmeta(Author).field_map["name"]
        field_title = getmeta(Book).field_map["title"]
        target = helpers.ValidationErrorCollection()
        target.add_message(field_name, "this is required")

        # Act & Assert
        assert field_name in target
        assert field_title not in target

    def test_getitem__with_string_field_name(self):
        # Arrange
        target = helpers.ValidationErrorCollection()
        target.add_message("name", "msg1", "msg2")

        # Act
        result = target["name"]

        # Assert
        assert result == ["msg1", "msg2"]

    def test_getitem__with_field_instance(self):
        # Arrange
        field = getmeta(Author).field_map["name"]
        target = helpers.ValidationErrorCollection()
        target.add_message(field, "this is required")

        # Act
        result = target[field]

        # Assert
        assert result == ["this is required"]

    def test_getitem__when_field_not_present(self):
        # Arrange
        target = helpers.ValidationErrorCollection()

        # Act
        result = target["unknown"]

        # Assert
        assert result == []

    def test_iter(self):
        # Arrange
        target = helpers.ValidationErrorCollection()
        target.add_message("name", "this is required")
        target.add_message("title", "too short")

        # Act
        result = list(target)

        # Assert
        assert result == ["name", "title"]

    def test_messages__with_valid_message(self):
        # Arrange
        target = helpers.ValidationErrorCollection()

        # Act
        target.add_message("name", "this is required")

        # Assert
        assert target.messages == {"name": ["this is required"]}

    def test_messages__with_empty_messages(self):
        # Arrange
        target = helpers.ValidationErrorCollection()

        # Act
        target.add_message("name")

        # Assert
        assert target.messages == {}

    def test_message_count__when_empty(self):
        # Arrange
        target = helpers.ValidationErrorCollection()

        # Act
        result = target.message_count

        # Assert
        assert result == 0

    def test_message_count__with_multiple_messages(self):
        # Arrange
        target = helpers.ValidationErrorCollection()
        target.add_message("name", "msg1", "msg2")
        target.add_message("title", "msg3")

        # Act
        result = target.message_count

        # Assert
        assert result == 3

    def test_add_message__with_string_field_name(self):
        # Arrange
        target = helpers.ValidationErrorCollection()

        # Act
        target.add_message("name", "this is required")

        # Assert
        assert target.messages == {"name": ["this is required"]}

    def test_add_message__with_field_instance(self):
        # Arrange
        field = getmeta(Author).field_map["name"]
        target = helpers.ValidationErrorCollection()

        # Act
        target.add_message(field, "this is required")

        # Assert
        assert target.messages == {"name": ["this is required"]}

    def test_add_message__with_none_field(self):
        # Arrange
        target = helpers.ValidationErrorCollection()

        # Act
        target.add_message(None, "resource level error")

        # Assert
        assert target.messages == {NON_FIELD_ERRORS: ["resource level error"]}

    def test_add_message__with_empty_messages(self):
        # Arrange
        target = helpers.ValidationErrorCollection()

        # Act
        target.add_message("name")

        # Assert
        assert target.messages == {}

    def test_add_message__multiple_calls_appends_messages(self):
        # Arrange
        target = helpers.ValidationErrorCollection()

        # Act
        target.add_message("name", "first")
        target.add_message("name", "second")

        # Assert
        assert target.messages == {"name": ["first", "second"]}

    def test_add_resource_message(self):
        # Arrange
        target = helpers.ValidationErrorCollection()

        # Act
        target.add_resource_message("this is required")

        # Assert
        assert target.messages == {NON_FIELD_ERRORS: ["this is required"]}

    def test_add_resource_message__with_empty_messages(self):
        # Arrange
        target = helpers.ValidationErrorCollection()

        # Act
        target.add_resource_message()

        # Assert
        assert target.messages == {}

    def test_add_error__with_validation_error_message_dict(self):
        # Arrange
        target = helpers.ValidationErrorCollection()
        error = ValidationError(
            {"name": ["Name is required"], "title": ["Title is required"]}
        )

        # Act
        target.add_error("ignored", error)

        # Assert
        assert target.messages == {
            "name": ["Name is required"],
            "title": ["Title is required"],
        }

    def test_add_error__with_validation_error_messages_list(self):
        # Arrange
        target = helpers.ValidationErrorCollection()
        error = ValidationError(["Single error"])

        # Act
        target.add_error("name", error)

        # Assert
        assert target.messages == {"name": ["Single error"]}

    def test_add_error__with_validation_error_messages_list_and_none_field(self):
        # Arrange
        target = helpers.ValidationErrorCollection()
        error = ValidationError(["Resource error"])

        # Act
        target.add_error(None, error)

        # Assert
        assert target.messages == {NON_FIELD_ERRORS: ["Resource error"]}

    def test_clear(self):
        # Arrange
        target = helpers.ValidationErrorCollection()
        target.add_message("name", "this is required")

        # Act
        target.clear()

        # Assert
        assert target.messages == {}
        assert bool(target) is False
        assert len(target) == 0

    def test_context_manager__when_no_errors(self):
        # Arrange
        target = helpers.ValidationErrorCollection()

        # Act & Assert - should not raise
        with target as errors:
            pass

        assert bool(errors) is False

    def test_context_manager__when_errors_added(self):
        # Arrange
        target = helpers.ValidationErrorCollection()

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info, target as errors:
            errors.add_message("name", "this is required")

        assert exc_info.value.message_dict == {"name": ["this is required"]}

    def test_context_manager__when_other_exception_raised(self):
        # Arrange
        target = helpers.ValidationErrorCollection()

        # Act & Assert - original exception should propagate without being replaced
        with pytest.raises(ValueError, match="Custom error"), target as errors:
            errors.add_message("name", "this is required")
            raise ValueError("Custom error")

    def test_raise_if_defined__with_no_errors(self):
        # Arrange
        target = helpers.ValidationErrorCollection()

        # Act & Assert - Nothing should happen
        target.raise_if_defined()

    def test_raise_if_defined__with_errors(self):
        # Arrange
        target = helpers.ValidationErrorCollection()
        target.add_message("name", "this is required")

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            target.raise_if_defined()

        assert exc_info.value.message_dict == {"name": ["this is required"]}

    def test_validation_error(self):
        # Arrange
        target = helpers.ValidationErrorCollection()
        target.add_message("name", "this is required")

        # Act
        error = target.validation_error()

        # Assert
        assert isinstance(error, ValidationError)
        assert error.message_dict == {"name": ["this is required"]}
