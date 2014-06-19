########
Adapters
########

Adapters are wrappers around resources that allow for an alternate view of the data contained in a resource or provide
additional functionality that is specific to part of your code base. A good example use-case is with your UI, you might
wish to add additional methods specific to rendering a resource but do not want additional layers of mapping or to
directly modify the base resource that is shared with other subsystems.

Quick Example
=============

Given the resource for a book, we wish to include a method to generate HTML.::

    import odin

    class Book(odin.Resource):
        title = odin.StringField()
        genre = odin.StringField()
        num_pages = odin.IntegerField()


    class BookUIAdapter(odin.ResourceAdapter):
        def to_html(self):
            return '<article><h1>%s</h1><p class="genre">%s</p></article>' % (self.title, self.genre)

    book = Book(title="Consider Phlebas", genre="Space Opera", num_pages=471)
    ui_book = BookUIAdapter(book)
    print(ui_book.to_html())

A second example is where when defining an API you wish to limit what fields are available.::

    import odin
    from odin.codecs import json_codec

    class User(odin.Resource):
        username = odin.StringField()
        first_name = oding.StringField()
        last_name = oding.StringField()
        password = oding.StringField()


    user = User(username='example', first_name='Joan', last_name='Doe', password='fjsk3is9z')
    api_user = odin.ResourceAdapter(user, exclude=('password',))

    json_codec.dumps(api_user)

Adapters provide the same interface as regular resources and can therefore be used with codecs.
