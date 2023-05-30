import datetime
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).parent
SRC = HERE.parent / "src"
sys.path.insert(0, SRC.as_posix())

import odin.datetimeutil  # noqa

ARE_YOU_EXPERIENCED = datetime.date(1967, 5, 12)
MWT = odin.datetimeutil.FixedTimezone(-6, "Mountain War Time")
BOOM = datetime.datetime(1945, 7, 16, 5, 29, 45, 0, MWT)


@pytest.fixture
def fixture_path():
    return HERE / "fixtures"
