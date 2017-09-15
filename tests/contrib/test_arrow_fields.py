import arrow
import datetime
import pytest

from odin.datetimeutil import utc
from odin.exceptions import ValidationError

try:
    from odin.contrib.arrow.fields import ArrowField
except ImportError:
    pass  # Arrow is not available
else:

    class TestArrowField(object):
        @pytest.mark.parametrize('kwargs, value, expected', (
            ({'null': True}, None, None),
            ({}, '2013-11-24', arrow.Arrow(2013, 11, 24)),
            ({}, '2013-11-24T18:43:00.000', arrow.Arrow(2013, 11, 24, 18, 43)),
            ({}, '2013-11-24T18:43:00.000Z', arrow.Arrow(2013, 11, 24, 18, 43)),
            ({}, arrow.Arrow(2013, 11, 24, 18, 43), arrow.Arrow(2013, 11, 24, 18, 43)),
            ({}, datetime.datetime(2013, 11, 24, 18, 43), arrow.Arrow(2013, 11, 24, 18, 43)),
            ({}, datetime.datetime(2013, 11, 24, 18, 43, 0, 0, utc), arrow.Arrow(2013, 11, 24, 18, 43)),
        ))
        def test_arrowfield__clean__valid(self, kwargs, value, expected):
            target = ArrowField(**kwargs)
            actual = target.clean(value)

            assert actual == expected

        @pytest.mark.parametrize('kwargs, value', (
            ({}, None),
            ({}, 123),
            ({}, '2013-11-'),
        ))
        def test_arrowfield__clean__invalid(self, kwargs, value):
            with pytest.raises(ValidationError):
                ArrowField(**kwargs).clean(value)
