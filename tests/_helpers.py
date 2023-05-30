import json

import pytest


def assertJSONEqual(raw, expected_data, msg=None):
    """
    Assert that two JSON documents are the same.
    """
    try:
        data = json.loads(raw)
    except ValueError:
        pytest.fail(f"First argument is not valid JSON: {raw!r}")
    else:
        if isinstance(expected_data, str):
            try:
                expected_data = json.loads(expected_data)
            except ValueError:
                pytest.fail(f"Second argument is not valid JSON: {expected_data!r}")

        if data != expected_data:
            pytest.fail(msg)
