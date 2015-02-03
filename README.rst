#####################################
Odin - Object Data Mapping for Python
#####################################

Odin provides a declarative framework for defining resources (classes) and their relationships, validation of the fields
that make up the resources and mapping between objects (either a resource, or other python structures).

Odin also comes with built in serialisation tools for importing and exporting data from resources.

.. image:: https://pypip.in/license/odin/badge.png
    :target: https://pypi.python.org/pypi/odin/
    :alt: License

.. image:: https://pypip.in/v/odin/badge.png
    :target: https://pypi.python.org/pypi/odin/

.. image:: https://travis-ci.org/timsavage/odin.png?branch=master
    :target: https://travis-ci.org/timsavage/odin
    :alt: Travis CI Status

.. image:: https://coveralls.io/repos/timsavage/odin/badge.png?branch=master
    :target: https://coveralls.io/r/timsavage/odin?branch=master
    :alt: Coveralls

.. image:: https://requires.io/github/timsavage/odin/requirements.png?branch=master
    :target: https://requires.io/github/timsavage/odin/requirements/?branch=master
    :alt: Requirements Status

.. image:: https://img.shields.io/badge/gitterim-timsavage.odin-brightgreen.svg?style=flat
    :target: https://gitter.im/timsavage/odin
    :alt: Gitter.im

Highlights
**********

* Class based declarative style
* Fields for building composite resources
* Field and Resource level validation
* Mapping between resources or extended to other object types (eg Django Models)
* Easy extension to support custom fields
* Python 2.7+, Python 3.3+ and PyPy :sup:`1` supported
* Integration with Django (see `baldr <https://github.com/timsavage/baldr>`_)
* Minimal dependencies (base functionality only requires *six*)

:sup:`1` certain contrib items are not supported. Pint is not installable with PyPy.


Quick links
***********

* `Documentation <https://odin.readthedocs.org/en/latest/>`_
* `Project home <https://github.com/timsavage/odin>`_
* `Issue tracker <https://github.com/timsavage/odin/issues>`_


Upcoming features
*****************

**In development**

* Customisable generation of documentation of resources (for integration into `Sphinx <http://sphinx-doc.org/>`_)
* XML Codec (export completed)
* Complete documentation, this will pretty much always be here.
* Improvements for CSV Codec (writing, reading multi resource CSV's)
* RESTful interface with support for Flask and Django see (see `baldr <https://github.com/timsavage/baldr>`_)
* Integration with other libraries (ie `Django <https://www.djangoproject.com/>`_ Models/Forms) (see `baldr <https://github.com/timsavage/baldr>`_)

**Planning**

* YAML codec


Requires
********

* six

**Optional**

* simplejson - Odin will use simplejson if it is available or fallback to the builtin json library
* msgpack-python - To enable use of the msgpack codec

**Contrib**

* jinja2 >= 2.7 - For documentation generation
* pint - Support for physical quantities using the `Pint <http://pint.readthedocs.org/>`_ library.


Example
*******

**With definition:**
::

    import odin

    class Author(odin.Resource):
        name = odin.StringField()

    class Publisher(odin.Resource):
        name = odin.StringField()

    class Book(odin.Resource):
        title = odin.StringField()
        authors = odin.ArrayOf(Author)
        publisher = odin.DictAs(Publisher)
        genre = odin.StringField()
        num_pages = odin.IntegerField()

::

    >>> b = Book(
            title="Consider Phlebas",
            genre="Space Opera",
            publisher=Publisher(name="Macmillan"),
            num_pages=471
        )
    >>> b.authors.append(Author(name="Iain M. Banks"))
    >>> from odin.codecs import json_codec
    >>> json_codec.dumps(b, pretty_print=True)
    {
        "$": "Book",
        "authors": [
            {
                "$": "Author",
                "name": "Iain M. Banks"
            }
        ],
        "genre": "Space Opera",
        "num_pages": 471,
        "publisher": {
            "$": "Publisher",
            "name": "Macmillan"
        },
        "title": "Consider Phlebas"
    }


Authors
*******

Tim Savage

Special Mention
***************

I would like to acknowledge the strong influence on the design of Odin from the Django ORM and it's notable contributor
Malcolm Tredinnick. He was a valued colleague who's untimely passing left a large void in our company and the wider
community.
