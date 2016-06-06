import json
import pytest
import six


def assertJSONEqual(raw, expected_data, msg=None):
    """
    Assert that two JSON documents are the same.
    """
    try:
        data = json.loads(raw)
    except ValueError:
        pytest.fail("First argument is not valid JSON: %r" % raw)
    else:
        if isinstance(expected_data, six.string_types):
            try:
                expected_data = json.loads(expected_data)
            except ValueError:
                pytest.fail("Second argument is not valid JSON: %r" % expected_data)

        if data != expected_data:
            pytest.fail(msg)
