# Disable logging if an explicit handler is not added
import logging
logging.getLogger('odin.registration').addHandler(logging.NullHandler())

from odin.__version__ import __version__
from odin.fields import *  # noqa
from odin.fields.composite import *  # noqa
from odin.fields.future import *  # noqa
from odin.fields.virtual import *  # noqa
from odin.mapping import *  # noqa
from odin.resources import Resource  # noqa
from odin.adapters import ResourceAdapter  # noqa
from odin.proxy import ResourceProxy  # noqa

__authors__ = "Tim Savage <tim@savage.company>"
__copyright__ = "Copyright (C) 2019 Tim Savage"
version_info = tuple(int(p) for p in __version__.split("."))
