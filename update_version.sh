#!/bin/bash
# Quick script to aid the updating of version numbers across the library, setup.py and documentation

sed -i "s/version=\"[.0-9]*\"/version=\"$1\"/g" setup.py
sed -i "s/release = '[.0-9]*'/release = '$1'/g" doc/conf.py
sed -i "s/__version__ = \"[.0-9]*\"/__version__ = \"$1\"/g" src/odin/__init__.py

