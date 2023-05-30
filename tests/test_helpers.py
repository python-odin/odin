import pytest

from odin import helpers
from odin.exceptions import ValidationError
from odin.utils import getmeta

from .resources import Author


class TestValidationErrorCollection:
    def test_messages__with_valid_message(self):
        target = helpers.ValidationErrorCollection()

        target.add_message("name", "this is required")

        assert target.messages == {"name": ["this is required"]}

    def test_messages__with_empty_messages(self):
        target = helpers.ValidationErrorCollection()

        target.add_message("name")

        assert target.messages == {}

    def test_add_message__with_string_field_name(self):
        target = helpers.ValidationErrorCollection()

        target.add_message("name", "this is required")

        assert target.messages == {"name": ["this is required"]}

    def test_add_message__with_field_instance(self):
        field = getmeta(Author).field_map["name"]
        target = helpers.ValidationErrorCollection()

        target.add_message(field, "this is required")

        assert target.messages == {"name": ["this is required"]}

    def test_add_resource_message(self):
        target = helpers.ValidationErrorCollection()

        target.add_resource_message("this is required")

        assert target.messages == {"__all__": ["this is required"]}

    def test_raise_if_defined__with_no_errors(self):
        target = helpers.ValidationErrorCollection()

        # Nothing should happen
        target.raise_if_defined()

    def test_raise_if_defined__with_errors(self):
        target = helpers.ValidationErrorCollection()
        target.add_message("name", "this is required")

        with pytest.raises(ValidationError):
            target.raise_if_defined()
