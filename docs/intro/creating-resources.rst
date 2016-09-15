##################
Creating resources
##################

Odin was designed to solve several common development problems:

* Loading data from file or data stream and converting into an object graph
* Validating data to ensure it meets the parameters of the program
* Mapping/transforming data into a different format or structure
* Do all of the above in a way that is easy to maintain, read and test

The goal of this document is to give you an overview of how to use the tools provided by Odin to accomplish the goals
set out in the previous paragraph.

Design your resources
=====================

The resource syntax offers many rich ways of representing your resources. Here's a quick example::

    import odin

    class Author(odin.Resource):
        name = odin.StringField()

    class Book(odin.Resource):
        title = odin.StringField()
        author = odin.DictAs(Author)
        genre = odin.StringField(max_length=255)
        num_pages = odin.IntegerField(min_value=1)


From this we can see that a resource is a collection of fields, each field maps to a specific data type and accepts
options that describe validation rules and how data is handled.

The above example also demonstrates relationships between the two resources. This simple example allows for an other
object to be attached to a book. With these simple primitives complex data-structures can be built.

Working with resources
======================

With a resource defined the API can be used to work with resources::

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

