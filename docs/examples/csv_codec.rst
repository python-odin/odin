##################
CSV Codec Examples
##################

The CSV codec is different to other codecs in that it produces an iterable of
:class:`odin.Resource` objects rather than a single structure.

Typical Usage
=============

When using the :mod:`odin.codecs.csv_codec` my recommendation is to define
your CSV file format using a CSV :class:`csv.Dialect` and a sub-class of the
:class:`odin.codecs.csv_codec.Reader` to configure how files are handled.

A simple example of a customised :class:`csv.Dialect` and
:class:`odin.codecs.csv_codec.Reader`::

    import csv

    from odin.codecs import csv_codec


    class MyFileDialect(csv.Dialect):
        """
        Custom CSV dialect
        """
        delimiter = '\t'       # Tab delimited
        quotechar = '"'        # Double quotes for quoting
        lineterminator = '\n'  # UNIX style line termination


    class MyFileReader(csv_codec.Reader):
        """
        Custom file reader
        """
        # Specify our custom dialect
        csv_dialect = MyFileDialect
        # Header case is not important
        ignore_header_case = True
        # Treat empty values as `None`
        default_empty_value = None

This can then be used with::

    # To read a file
    with open("my_file.csv") as f:
        for r in MyFileReader(f, MyResource):
            pass

    # To write a file
    with open("my_file.csv", "w") as f:
        csv_codec.dump(f, my_resources, dialect=MyFileDialect)


Handling errors
===============

As resources are generated as each CSV row is read any validation errors raised
also need to be handled. The default behavior is for a validation error to be
raised when a invalid row is encountered effectively stopping processing.
However, it may be valid to skip bad rows or, a report of bad rows can be
generated and processing continued.

There are two approaches that can be used:

1. Provide an ``error_callback`` value to the :class:`odin.codecs.csv_codec.Reader`
2. Sub-class the :class:`odin.codecs.csv_codec.Reader` class and implement a
    custom ``handle_validation_error`` method to process errors.

.. note::
    Providing an ``error_callback`` will overwrite any custom
    ``handle_validation_error`` method.

The ``error_callback`` option is the simplest::

    def error_callback(validation_error, idx):
        """
        Handle errors reading rows from CSV file.

        :param validation_error: The validation error exception
        :param idx: The row index the error occurred on.
        :returns: ``None`` or ``False`` to explicitly case the exception to
            be raised.

        """
        print("Error in row {}: {}".format(idx, validation_error), file=sys.stderr)

    with open("my_file.csv") as f:
        for r in MyFileReader(f, MyResource, error_callback=error_callback):
            ...


The sub-class method is more involved upfront but does allow for more
customisation::

    class MyReader(csv_codec.Reader):
        """
        Custom file reader that reports errors to a file.
        """
        def __init__(self, f, error_file, *args, **kwargs):
            super().__init__(self, *args, **kwargs)

            self.error_file = error_file

        def handle_validation_error(self, validation_error, idx):
            self.error_file.write("{}\t{}\n".format(idx, validation_error))


    with open("my_file.csv") as f_in, open("my_file.error.csv", "w") as f_err:
        for r in MyReader(f_in, f_err, MyResource):
            ...

The second option allows for a lot of customisation and reuses. For example the
error report could itself output a CSV file.
