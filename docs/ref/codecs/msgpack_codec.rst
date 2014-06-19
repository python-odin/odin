#################
MessagePack Codec
#################

Codec for serialising and de-serialising data in `MessagePack <http://msgpack.org>`_ format. Supports both array and
objects for mapping into resources or collections of resources.

The MessagePack codec uses the :py:mod:`msgpack-python` module.

.. automodule:: odin.codecs.msgpack_codec

Methods
=======

    .. autofunction:: load

    .. autofunction:: loads

    .. autofunction:: dump

    .. autofunction:: dumps


Customising Encoding
====================

Serialisation of Odin resources is handled by a customised :py:class:`msgpack.Packer`. Additional data types can be
appended to the :py:const:`odin.codecs.msgpack_codec.TYPE_SERIALIZERS` dictionary.

Example usage
=============

Loading a resource from a file::

    from odin.codecs import msgpack_codec

    with open('my_resource.msgp') as f:
        resource = msgpack_codec.load(f)

