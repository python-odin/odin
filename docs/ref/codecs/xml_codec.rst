#########
XML Codec
#########

Codec for serialising and de-serialising XML data. Supports both array and objects for mapping into resources or
collections of resources.

.. automodule:: odin.codecs.xml_codec

Methods
=======

    .. autofunction:: dump

    .. autofunction:: dumps


Unsupported Fields
==================

There is no direct representation for a :py:class:`odin.fields.DictField`.


Example usage
=============

Loading a resource from a file::

    from odin.codecs import xml_codec

    with open('my_resource.xml') as f:
        resource = xml_codec.load(f)


Saving a resource to a file::

    from odin.codecs import xml_codec

    with open('my_resource.xml', 'w') as f:
        xml_codec.dump(f, resource)
