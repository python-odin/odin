import sys
import pytest

from odin.utils import getmeta

# Workaround to ensure testsuite works on Python < 3.6
try:
    from tests.new_resources import Book
except SyntaxError:
    if sys.version_info < (3, 6):
        pytest.skip("Requires Python 3.6 or higher", allow_module_level=True)
    else:
        raise


class TestNewResourceType:
    def test_fields_are_identified_in_correct_order(self):
        meta = getmeta(Book)

        assert [f.name for f in meta.fields] == [
            "title",
            "isbn",
            "num_pages",
            "rrp",
            "fiction",
            "genre",
            "published",
            "authors",
            "publisher",
        ]
