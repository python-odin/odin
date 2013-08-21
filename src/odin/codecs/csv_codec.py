# -*- coding: utf-8 -*-
"""
Parse CSV files into Odin Resources
"""
import csv
from odin.resources import create_resource_from_dict


class ResourceReader(csv.DictReader):
    def __init__(self, f, resources, *args, **kwargs):
        self.resources = resources
        csv.DictReader.__init__(self, f, *args, **kwargs)

    # Python 2
    def next(self):
        d = csv.DictReader.next(self)
        return create_resource_from_dict(d, self.resources._meta.resource_name)

    # Python 3
    def __next__(self):
        d = csv.DictReader.__next__(self)
        return create_resource_from_dict(d, self.resources._meta.resource_name)
