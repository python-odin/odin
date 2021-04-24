# Disable logging if an explicit handler is not added
import logging

logging.getLogger("odin.registration").addHandler(logging.NullHandler())

from odin.fields import *  # noqa
from odin.fields.composite import *  # noqa
from odin.fields.future import *  # noqa
from odin.fields.virtual import *  # noqa
from odin.mapping import *  # noqa
from odin.resources import Resource  # noqa
from odin.adapters import ResourceAdapter  # noqa
from odin.proxy import ResourceProxy  # noqa

__authors__ = "Tim Savage <tim@savage.company>"
__copyright__ = "Copyright (C) 2021 Tim Savage"
