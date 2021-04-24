##########
TOML Codec
##########

Codec for serialising and de-serialising TOML data. Supports both array and objects for mapping into resources or
collections of resources.

The TOML codec uses the :py:mod:`toml` module.

.. automodule:: odin.codecs.toml_codec

Methods
=======

    .. autofunction:: load

    .. autofunction:: loads

    .. autofunction:: dump

    .. autofunction:: dumps


Customising Encoding
====================

Serialisation of Odin resources is handled by a customised :py:class:`toml.Encoder`. Additional data types can be
appended to the :py:const:`odin.codecs.toml_codec.TOML_TYPES` dictionary.

Example usage
=============

Loading a resource from a file::

    from odin.codecs import toml_codec

    with open('my_resource.toml') as f:
        resource = toml_codec.load(f)

