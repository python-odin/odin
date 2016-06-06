##########
YAML Codec
##########

Codec for serialising and de-serialising YAML data. Supports both array and objects for mapping into resources or
collections of resources.

The YAML codec uses the :py:mod:`yaml` module and uses the compiled C versions of the library if available.

.. automodule:: odin.codecs.yaml_codec

Methods
=======

    .. autofunction:: load

    .. autofunction:: loads

    .. autofunction:: dump

    .. autofunction:: dumps


Customising Encoding
====================

Serialisation of Odin resources is handled by a customised :py:class:`yaml.Dumper`. Additional data types can be
appended to the :py:const:`odin.codecs.yaml_codec.YAML_TYPES` dictionary.

Example usage
=============

Loading a resource from a file::

    from odin.codecs import yaml_codec

    with open('my_resource.yaml') as f:
        resource = yaml_codec.load(f)

