# -*- coding: utf-8 -*-
import six
import csv

from odin import bases
from odin.fields import NOT_PROVIDED
from odin.resources import create_resource_from_iter, create_resource_from_dict
from odin.mapping import MappingResult
from odin.utils import getmeta

CONTENT_TYPE = 'text/csv'


def reader(f, resource, includes_header=False, csv_module=csv, full_clean=True, *args, **kwargs):
    """
    CSV reader that returns resource objects

    :param f: file like object
    :param resource:
    :param includes_header: File includes a header that should be used to map columns
    :param csv_module: Specify an alternate csv module (eg unicodecsv); defaults to the builtin csv as this module
        is implemented in C.
    :param full_clean: Perform a full clean on each object
    :return: Iterable reader object

    """
    csv_reader = csv_module.reader(f, *args, **kwargs)
    if includes_header:
        fields = getmeta(resource).fields

        # Pre-generate field mapping
        header = csv_reader.next()
        mapping = []
        for field in fields:
            if field.name in header:
                mapping.append(header.index(field.name))
            else:
                mapping.append(None)

        # Iterate CSV and process input
        for row in csv_reader:
            yield create_resource_from_iter(
                (NOT_PROVIDED if s is None else row[s] for s in mapping), resource, full_clean
            )

    else:
        # Iterate CSV and process input
        for row in csv_reader:
            yield create_resource_from_iter(
                (NOT_PROVIDED if col is None else col for col in row), resource, full_clean
            )


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


def value_fields(resource):
    """
    Iterator to get non-composite (eg value) fields for export
    """
    meta = resource._meta  # noqa - Accessing a "protected" field is required in this case
    return [f for f in meta.all_fields if f not in meta.composite_fields]


def _get_resource_type(resources, resource_type):
    if isinstance(resources, bases.TypedResourceIterable):
        # Use first resource to obtain field list
        return resource_type or resources.resource_type
    elif isinstance(resources, bases.ResourceIterable) and resource_type:
        return resource_type
    elif isinstance(resources, (list, tuple)):
        if not len(resources):
            return
        # Use first resource to obtain field list
        return resource_type or resources[0]
    else:
        raise Exception("Not supported input format")


def dump_to_writer(writer, resources, resource_type=None, fields=None):
    """
    Dump resources to a CSV writer interface.

    The interface should expose the :py:class:`csv.writer` interface.

    :type writer: :py:class:`csv.writer`
    :param writer: Writer object
    :param fields: List of fields to write
    :param resources: Collection of resources to dump.
    :param resource_type: Resource type to use for CSV columns; if None the first resource will be used.
    :returns: List of fields that where written to.

    """
    resource_type = resource_type or _get_resource_type(resources, resource_type)

    if not fields:
        fields = value_fields(resource_type)

    # Iterate resources and write to CSV
    for resource in resources:
        row = [field.prepare(field.value_from_object(resource)) for field in fields]
        writer.writerow(row)

    return fields


def dump(f, resources, resource_type=None, include_header=True, cls=csv.writer, **kwargs):
    """
    Dump resources into a CSV file.

    :param f: File to dump to.
    :param resources: Collection of resources to dump.
    :param resource_type: Resource type to use for CSV columns; if None the first resource will be used.
    :param include_header: Write a CSV header.
    :param cls: Writer to use when writing CSV, this should be based on :class:`csv.writer`.
    :param kwargs: Additional parameters to be supplied to the writer instance.

    """
    resource_type = _get_resource_type(resources, resource_type)

    fields = value_fields(resource_type)

    # Setup CSV
    writer = cls(f, **kwargs)

    # Write header
    if include_header:
        writer.writerow([field.name for field in fields])

    dump_to_writer(writer, resources, resource_type, fields)


def dumps(resources, resource_type=None, cls=csv.writer, **kwargs):
    """
    Dump output to a string

    :param resources:
    :param resources: Collection of resources to dump.
    :param resource_type: Resource type to use for CSV columns; if None the first resource will be used.
    :param cls: Writer to use when writing CSV, this should be based on :class:`csv.writer`.
    :param kwargs: Additional parameters to be supplied to the writer instance.

    """
    buf = six.StringIO.StringIO()
    dump(buf, resources, resource_type, cls, **kwargs)
    return buf.getvalue()
