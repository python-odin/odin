# -*- coding: utf-8 -*-
import csv
from odin.resources import create_resource_from_dict

CONTENT_TYPE = 'text/csv'


class ResourceReader(csv.DictReader):
    def __init__(self, f, resource, *args, **kwargs):
        self.resource = resource
        csv.DictReader.__init__(self, f, *args, **kwargs)

    # Python 2
    def next(self):
        return create_resource_from_dict(csv.DictReader.next(self), self.resource, copy_dict=False)

    # Python 3
    def __next__(self):
        return create_resource_from_dict(csv.DictReader.__next__(self), self.resource, copy_dict=False)
