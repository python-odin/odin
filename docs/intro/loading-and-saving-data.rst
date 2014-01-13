#######################
Loading and saving data
#######################

Saving and loaded of resources is handled by codecs for each format.

JSON data
=========

JSON data is loaded and saved using the :py:mod:`odin.codecs.json_codec` module. This module exposes an API that is very
similar to Pythons built in :py:mod:`json` module.

Using the Book and Author resources presented in the :doc:`creating-resources` section::

    # Import the resources we created from our "library" app
    >>> from library.resources import Author, Book

    # Create an instance of an Author
    >>> a = Author(name="Iain M. Banks")

    # Create an instance of a Book
    >>> b = Book(title="Consider Phlebas", author=a, genre="Space Opera", num_pages=471)

    # Dump as a JSON encoded string
    from odin.codecs import json_codec
    >>> json_codec.dumps(b)
    '{"genre": "Space Opera", "title": "Consider Phlebas", "num_pages": 471, "$": "library.resources.Book", "author": {
    "name": "Iain M. Banks", "$": "library.resources.Author"}}'

.. note::
    Note the **$** entries. The **$** symbol is used to keep track of an objects type in the serialised state and to aid
    deserialization of data.

Similarly data can be deserialized back into an object graph using the :py:meth:`odin.codecs.json_codec.loads` method.
