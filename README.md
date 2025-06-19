# Odin

Odin provides a declarative framework for defining resources (classes) and their relationships, validation of the fields
that make up the resources and mapping between objects (either a resource, or other python structures).

Odin also comes with built in serialisation tools for importing and exporting data from resources.

<table>
<tr>
    <th>Docs/Help</th>
    <td>
        <a href="https://odin.readthedocs.org/">
            <img src="https://readthedocs.org/projects/odin/badge/?version=latest" 
                alt="ReadTheDocs" />
        </a>
        <a href="https://gitter.im/timsavage/odin">
            <img src="https://img.shields.io/badge/gitterim-timsavage.odin-brightgreen.svg?style=flat " 
                alt="Gitter.im" />
        </a>
    </td>
</tr>
<tr>
    <th>Build</th>
    <td>
        <a href="https://github.com/python-odin/odin/actions/workflows/release.yml">
            <img src="https://github.com/python-odin/odin/actions/workflows/release.yml/badge.svg" 
                alt="Python package" />
        </a>
    </td>
</tr>
<tr>
    <th>Quality</th>
    <td>
        <a href="https://sonarcloud.io/dashboard?id=python-odin_odin">
            <img src="https://sonarcloud.io/api/project_badges/measure?project=python-odin_odin&metric=sqale_rating" 
                alt="Maintainability" />
        </a>
        <a href="https://sonarcloud.io/project/security_hotspots">
            <img src="https://sonarcloud.io/api/project_badges/measure?project=python-odin_odin&metric=security_rating" 
                alt="Security" />
        </a>
        <a href="https://sonarcloud.io/code?id=python-odin_odin">
            <img src="https://sonarcloud.io/api/project_badges/measure?project=python-odin_odin&metric=coverage" 
                alt="Coverage" />
        </a>
        <a href="https://github.com/ambv/black">
            <img src="https://img.shields.io/badge/code%20style-black-000000.svg" 
                alt="Once you go Black..." />
        </a>
    </td>
</tr>
<tr>
    <th>Package</th>
    <td>
        <a href="https://pypi.io/pypi/odin/">
            <img src="https://img.shields.io/pypi/v/odin" 
                alt="Latest Version" />
        </a>
        <a href="https://pypi.io/pypi/odin/">
            <img src="https://img.shields.io/pypi/pyversions/odin" />
        </a>
        <a href="https://pypi.io/pypi/odin/">
            <img src="https://img.shields.io/pypi/l/odin" />
        </a>
        <a href="https://pypi.io/pypi/odin/">
            <img src="https://img.shields.io/pypi/wheel/odin" 
                alt="PyPI - Wheel" />
        </a>
    </td>
</tr>
</table>

## Highlights

* Class based declarative style
* Class based annotations style! ✨ new in 2.0
* Fields for building composite resources
* Field and Resource level validation
* Easy extension to support custom fields
* Python 3.8+ and PyPy <sup>1</sup> supported
* Support for documenting resources with [Sphinx](http://sphinx-doc.org/)
* Minimal dependencies

<sup>1</sup> certain contrib items are not supported. Pint is not installable with PyPy.

## Use cases

* Design, document and validate complex (and simple!) data structures
* Convert structures to and from different formats such as JSON, YAML, MsgPack, CSV, TOML
* Validate API inputs
* Define message formats for communications protocols, like an RPC
* Map API requests to ORM objects

## Quick links

* [Documentation](https://odin.readthedocs.org/)
* [Project home](https://github.com/python-odin/odin)
* [Issue tracker](https://github.com/python-odin/odin/issues)


## Upcoming features

### In development

* XML Codec (export only)
* Complete documentation coverage
* Improvements for CSV Codec (writing, reading multi resource CSV's)


## Requires

### Optional

* simplejson - Odin will use simplejson if it is available or fallback to the builtin json library
* msgpack-python - To enable use of the msgpack codec
* pyyaml - To enable use of the YAML codec
* toml - To enable use of the TOML codec

### Contrib

* arrow - Support for Arrow data types.
* pint - Support for physical quantities using the [Pint](http://pint.readthedocs.org/) library.

### Development

* pytest - Testing
* pytest-cov - Coverage reporting

## Example

### Definition

```python
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
```

### Using Annotations

```python
import odin

class Author(odin.AnnotatedResource):
    name: str

class Publisher(odin.AnnotatedResource):
    name: str
    website: odin.Url | None

class Book(odin.AnnotatedResource):
    title: str
    authors: list[Author]
    publisher: Publisher
    genre: str
    num_pages: int
```

### Usage

```pycon
>>> b = Book(
        title="Consider Phlebas",
        genre="Space Opera",
        publisher=Publisher(name="Macmillan"),
        num_pages=471
    )
>>> b.authors.append(Author(name="Iain M. Banks"))
>>> from odin.codecs import json_codec
>>> json_codec.dumps(b, indent=4)
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
```
