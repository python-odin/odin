#########
CSV Codec
#########

Codec for iterating a CSV file and parsing into a JSON.

Example
=======

Iterate a CSV file yielding resources::

    from odin.codecs import csv_codec

    with open('my_resources.csv') as f:
        for resource in csv_codec.ResourceReader(f, MyResource):
            print resource


Limitations
===========

The CSV codec works on list of single resources with each row being mapped to a resource object.