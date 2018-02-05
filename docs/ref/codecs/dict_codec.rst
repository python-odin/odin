##########
Dict Codec
##########

Codec for serialising and de-serialising Dictionary and List objects.

.. automodule:: odin.codecs.dict_codec

Methods
=======

    .. autofunction:: load

    .. autofunction:: dump


Example usage
=============

Loading a resource from a file::

    from odin.codecs import dict_codec

    my_dict = {}

    resource = dict_codec.load(my_dict, MyResource)
