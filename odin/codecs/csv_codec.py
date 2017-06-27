# -*- coding: utf-8 -*-
"""
CSV Codec
~~~~~~~~~

Codec for iterating a CSV file and parsing into a Resource.

The CSV codec is codec that yields multiple resources rather than a single document.
The CSV codec does not support nesting of resources.

Reading data from a CSV file::

    with open("my_file.csv") as f:
        with resource in csv_codec.reader(f, MyResource):
            ...

"""
import six
import csv

from odin import bases
from odin.compatibility import deprecated
from odin.datastructures import CaseLessStringList
from odin.fields import NOT_PROVIDED
from odin.resources import create_resource_from_iter, create_resource_from_dict
from odin.utils import getmeta, lazy_property
from odin.exceptions import CodecDecodeError, ValidationError

CONTENT_TYPE = 'text/csv'


class Reader(bases.TypedResourceIterable):
    """
    Customisable reader object.
    """
    csv_reader = csv.reader
    """
    CSV Reader object to use (if you wish to use *unicodecsv* or similar)
    """

    includes_header = True
    """
    File is expected to include a header.
    """

    ignore_header_case = False
    """
    Use case-less comparison on header fields.
    """

    strict_fields = False
    """
    Strictly check header fields.
    """

    csv_dialect = 'excel'
    """
    CSV Dialect to use; defaults to the CSV libraries default value of *excel*.
    """

    default_empty_value = ''
    """
    The default value to use if a field is empty. This can be used to default to *None*.
    """

    def __init__(self, f, resource_type, full_clean=True, error_callback=None, **reader_kwargs):
        """
        Initialise a reader

        :param f: Input file (or file like) object to read
        :param resource_type: Resource type to use as field template.
        :param full_clean: Perform a full clean on objects
        :param error_callback: Optional callback for errors
        :param reader_kwargs: kwargs to pass to the csv_reader

        """
        super(Reader, self).__init__(resource_type)
        self.full_clean = full_clean
        if error_callback:
            self.handle_validation_error = error_callback

        # Backwards compatibility
        for arg in ('csv_reader', 'includes_header', 'ignore_header_case', 'strict_fields', 'csv_dialect'):
            if arg in reader_kwargs:
                setattr(self, arg, reader_kwargs.pop(arg))

        # Create reader instance
        self._reader = self._create_reader(f, reader_kwargs)

        # Configure header
        if self.includes_header:
            self.header = self._read_header()

            # Handle strict fields
            if self.strict_fields and self.extra_field_names:
                raise CodecDecodeError("Extra unknown fields: {0}".format(','.join(self.extra_field_names)))

        # Built in counters
        self.row_count = None
        self.error_count = None

    def __iter__(self):
        # Reset error count
        self.error_count = 0

        # Local vars
        resource = self.resource_type
        full_clean = self.full_clean
        default_empty_value = self.default_empty_value
        handle_validation_error = getattr(self, 'handle_validation_error', None)
        idx = -1

        def create_resource(values, i):
            try:
                return create_resource_from_iter(
                    # Handle empty values
                    (default_empty_value if v == '' else v for v in values),
                    resource, full_clean
                )
            except ValidationError as ve:
                # Don't raise these through yield as will cause a StopIteration
                # even if validation error can be handled safely.
                self.error_count += 1
                if not handle_validation_error:
                    raise
                # If handle error explicitly returns False raise exception
                if handle_validation_error(ve, i) is False:
                    raise

        if self.includes_header:
            mapping = self.field_mapping

            for idx, row in enumerate(self._reader):
                # Check if row is less than mapping (as this will causes errors)!
                res = create_resource(
                    (s if s is NOT_PROVIDED else row[s] for s in mapping),
                    idx + 1)  # Add one to index as row "0" will be the header
                if res:
                    yield res
        else:
            for idx, row in enumerate(self._reader):
                res = create_resource(row, idx)
                if res:
                    yield res

        self.row_count = idx + 1  # Add one to get a count from the last index

    def _create_reader(self, f, kwargs):
        """
        Create internal reader instance

        :param f: File (or file like) object
        :param kwargs: Dictionary of additional keyword args
        :return: Reader instance

        """
        return self.csv_reader(f, self.csv_dialect, **kwargs)

    def _read_header(self):
        """
        Get the header, this needs to be called **once** only!
        """
        header = next(self._reader)
        if self.ignore_header_case:
            header = CaseLessStringList(header)
        return header

    @lazy_property
    def field_names(self):
        """
        Field names from resource.
        """
        fields = getmeta(self.resource_type).fields
        if self.ignore_header_case:
            return CaseLessStringList(field.name for field in fields)
        else:
            return tuple(field.name for field in fields)

    @lazy_property
    def extra_field_names(self):
        """
        Extra fields not included in header
        """
        return tuple(field for field in self.header if field not in self.field_names)

    @lazy_property
    def field_mapping(self):
        """
        Index mapping of CSV fields to resource fields.
        """
        mapping = []

        # Add expected fields
        header = self.header
        for name in self.field_names:
            if name in header:
                mapping.append(header.index(name))
            else:
                mapping.append(NOT_PROVIDED)

        # Append any extra fields
        for name in self.extra_field_names:
            mapping.append(header.index(name))

        return tuple(mapping)


def reader(f, resource, includes_header=False, csv_module=csv, full_clean=True,
           ignore_header_case=False, strict_fields=False, **kwargs):
    """
    CSV reader that returns resource objects

    :param f: file like object
    :param resource:
    :param includes_header: File includes a header that should be used to map columns
    :param csv_module: Specify an alternate csv module (eg unicodecsv); defaults to the builtin csv as this module
        is implemented in C.
    :param full_clean: Perform a full clean on each object
    :param ignore_header_case: Ignore the letter case on header
    :param strict_fields: Extra fields cannot be provided.
    :return: Iterable reader object
    :rtype: Reader

    """
    return Reader(f, resource, full_clean,
                  csv_reader=csv_module.reader,
                  includes_header=includes_header,
                  ignore_header_case=ignore_header_case,
                  strict_fields=strict_fields,
                  **kwargs)


@deprecated("This class will be removed in 1.1 migrate to the `reader` method.")
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
    meta = getmeta(resource)
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
