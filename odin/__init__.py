__authors__ = "Tim Savage"
__author_email__ = "tim@savage.company"
__copyright__ = "Copyright (C) 2014 Tim Savage"
__version__ = "0.10"

from odin.fields import *  # noqa
from odin.fields.composite import *  # noqa
from odin.fields.virtual import *  # noqa
from odin.mapping import *  # noqa
from odin.resources import Resource  # noqa
from odin.adapters import ResourceAdapter  # noqa

# Disable logging if an explicit handler is not added
try:
    import logging
    logging.getLogger('odin').addHandler(logging.NullHandler())
except AttributeError:
    pass  # Fallback for python 2.6
