#####################################
Odin - Object Data Mapping for Python
#####################################

Based off my previous library for mapping JSON to python objects Odin branches from just supporting JSON to supporting
many other data representations, allowing them to be mapped into converted into a Python object graph, validated against
a set of validators and mapped into other formats.

.. image:: https://travis-ci.org/timsavage/odin.png?branch=master
    :target: https://travis-ci.org/timsavage/odin
    :alt: Travis CI Status

Highlights
**********

* Class based declarative style
* Fields for building composite resources
* Field and Resource level validation
* Easy extension to support custom fields
* Python 2.7+ and Python 3.3+ supported


Quick links
***********

* `Documentation <https://odin.readthedocs.org/en/latest/>`_
* `Project home <https://github.com/timsavage/odin>`_
* `Issue tracker <https://github.com/timsavage/odin/issues>`_


Upcoming features
*****************

**In development**

* Customisable generation of documentation of resources (for integration into `Sphinx <http://sphinx-doc.org/>`_)
* Complete documentation (around 70-80% complete for current features)

**Planning**

* Integration with other libraries (ie `Django <https://www.djangoproject.com/>`_ Models/Forms)
* Support for CSV


Requires
********

* six

**Optional**

* jinja2 >= 2.7 - For documentation generation
* simplejson - Odin will use simplejson if it is available or fallback to the builtin json library


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
        publisher = odin.ObjectAs(Publisher)
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
    >>> odin.dumps(b, pretty_print=True)
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

