import sys
import pytest

from odin.utils import getmeta

# Workaround to ensure testsuite works on Python < 3.6
try:
    import odin.new_resource as new_resource
except SyntaxError:
    if sys.version_info < (3, 6):
        new_resource = None
    else:
        raise
else:
    from tests.new_resources import Book


@pytest.mark.skipif(new_resource is None, reason="Requires Python 3.6 or higher")
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
