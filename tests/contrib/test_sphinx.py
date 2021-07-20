import pytest

from odin import Resource
from odin.contrib import sphinx


class TestResourceDocumenter(object):
    @pytest.mark.parametrize(
        "type_, expected", ((1, False), ("EEk", False), (Resource, True),)
    )
    def test_can_document_member(self, type_, expected):
        actual = sphinx.ResourceDocumenter.can_document_member(type_)

        assert actual == expected
