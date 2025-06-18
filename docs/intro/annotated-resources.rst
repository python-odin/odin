###################
Annotated resources
###################

As of Odin 2.0, resources can now be defined using Python type annotations. This greatly simplifies definition of
resource structures while maintaining compatibility with all existing features. Types defined using the existing
`odin.Resource` base class can be used in conjunction with new annotation style resources.

Defining annotated resources
============================

The annotated resource syntax offers many rich ways of representing your resources. Here's a quick example:

.. code-block:: python

    import odin

    class Author(odin.AnnotatedResource):
        name: str

    class Book(odin.AnnotatedResource):
        title: str
        author: Author
        genre: Annotated[str | None, odin.Options(max_length=255)]
        num_pages: Annotated[int, odin.Options(min_value=1)]



.. tip:: If you prefer the shorthand `odin.AResource` can be used in place of `odin.AnnotatedResource`

From this we can see that a resource is a collection of fields, each field maps to a specific data type and accepts
options that describe validation rules and how data is handled.

The above example also demonstrates relationships between the two resources. This simple example allows for another
object to be attached to a book. With these simple primitives complex data-structures can be built.

Working with resources
======================

Just like any other resource the API behaves the same::

    # Import the resources we created from our "library" app
    >>> from library.resources import Author, Book

    # Create an instance of an Author
    >>> a = Author(name="Iain M. Banks")

    # Create an instance of a Book
    >>> b = Book(title="Consider Phlebas", author=a, genre="Space Opera", num_pages=471)
    >>> b
    <Book: library.resources.Book resource>

    # Fields are represented as attributes on the Python object.
    >>> b.title
    'Consider Phlebas'

    # DictAs fields are references to other resources.
    >>> b.author.name
    'Iain M. Banks'

    # Get all the data as a dict
    >>> a.to_dict()
    {'name': 'Iain M. Banks'}

    # Validate that the information entered is valid.
    # Create an instance of a Book
    >>> b = Book(title="Consider Phlebas", genre="Space Opera", num_pages=471)
    >>> b.full_clean()
    ValidationError: {'author': [{'name': ['This field cannot be null.']}]}



Abstract Resources
==================

Abstract resources no longer require the use of a ``Meta`` block then are identified through the use of a keyword
argument eg:

.. code-block:: python

    import odin

    class LibraryBase(odin.AnnotatedResource, abstract=True):
        """
        Common base class for library resources
        """
        name: str

    class Library(LibraryBase):
        address: str


The ``Library`` resource inherits the _name_ field from ``LibraryBase`` but cannot be instantiated directly itself.
