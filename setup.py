#!/usr/bin/env python
import os

from setuptools import setup

here = os.path.dirname(__file__)

# Read version file
about = {}
with open(os.path.join(here, "odin/__version__.py")) as f_in:
    exec(f_in.read(), about)

if __name__ == "__main__":
    setup(version=about["__version__"])
