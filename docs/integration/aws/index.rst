####################################
Integration with Amazon Web Services
####################################

Integration with `Amazon Web Services <https://aws.amazon.com>`_ is via
`odincontrib.aws <https://github.com/python-odin/odincontrib.aws/`

Requires ``boto3``.

Odin Contrib AWS includes:

* Integration with DynamoDB. Dynamo versions of fields, resources (Table) and querying


Dynamo DB
=========

Tables can be defined using extended Resources, this provides an interface for table creation, save (put) items, query,
scan and batch operations. Querying is performed either using raw parameters (as used by Boto3) or using a SQLAlchemy
style fluent interface.

Example::

    from odincontrib_aws import dynamodb


    class Book(dynamodb.Table):
        class Meta:
            namespace = 'library'

        title = dynamodb.StringField()
        isbn = dynamodb.StringField(key=True)
        num_pages = dynamodb.IntegerField()
        genre = dynamodb.StringField(choices=(
            ('sci-fi', 'Science Fiction'),
            ('fantasy', 'Fantasy'),
            ('biography', 'Biography'),
            ('others', 'Others'),
            ('computers-and-tech', 'Computers & technology'),
        ))

    session = dynamodb.Session()

    # Save a new book into a Dynamo DB table
    book = Book(
        title="The Hitchhiker's Guide to the Galaxy",
        isbn="0-345-39180-2",
        num_pages=224,
        genre='sci-fi',
    )
    session.put_item(book)

    # Scan through all books in the table (this method is transparently paged)
    for book in session.scan(Book):
        print(book.title)


SQS
===

This is development in progress to use Odin for defining and verifying SQS messages.
