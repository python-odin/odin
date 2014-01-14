# -*- coding: utf-8 -*-
import csv
from odin.resources import create_resource_from_dict


class ResourceReader(csv.DictReader):
    def __init__(self, f, resources, *args, **kwargs):
        self.resources = resources
        csv.DictReader.__init__(self, f, *args, **kwargs)

    # Python 2
    def next(self):
        return create_resource_from_dict(
            csv.DictReader.next(self),
            self.resources._meta.resource_name
        )

    # Python 3
    def __next__(self):
        return create_resource_from_dict(
            csv.DictReader.__next__(self),
            self.resources._meta.resource_name
        )
