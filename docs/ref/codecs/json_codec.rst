##########
JSON Codec
##########

Codec for serialising and de-serialising JSON data. Supports both array and objects for mapping into resources or
collections of resources.

The JSON codec uses the :py:mod:`simplejson` module if available and falls back to the :py:mod:`json` module
included in the Python standard library.

.. automodule:: odin.codecs.json_codec

Methods
=======

    .. autofunction:: load

    .. autofunction:: loads

    .. autofunction:: dump

    .. autofunction:: dumps


Customising Encoding
====================

Serialisation of Odin resources is handled by a customised :py:class:`json.Encoder`. Additional data types can be
appended to the :py:const:`odin.codecs.json_codec.JSON_TYPES` dictionary.

Example usage
=============

Loading a resource from a file::

    from odin.codecs import json_codec

    with open('my_resource.json') as f:
        resource = json_codec.load(f)

