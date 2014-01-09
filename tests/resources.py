# -*- coding: utf-8 -*-
import odin
from odin.mapping.helpers import sum_fields


class Author(odin.Resource):
    name = odin.StringField()

    class Meta:
        name_space = None


class Publisher(odin.Resource):
    name = odin.StringField()

    class Meta:
        name_space = None


class LibraryBook(odin.Resource):
    class Meta:
        abstract = True
        name_space = "library"


class Book(LibraryBook):
    title = odin.StringField()
    num_pages = odin.IntegerField()
    rrp = odin.FloatField()
    fiction = odin.BooleanField()
    genre = odin.StringField(choices=(
        ('sci-fi', 'Science Fiction'),
        ('fantasy', 'Fantasy'),
        ('biography', 'Biography'),
        ('others', 'Others'),
    ))
    published = odin.TypedArrayField(odin.DateTimeField())
    authors = odin.ArrayOf(Author)
    publisher = odin.DictAs(Publisher)


class Library(odin.Resource):
    name = odin.StringField()
    books = odin.ArrayOf(LibraryBook)

    class Meta:
        name_space = None


class OldBook(LibraryBook):
    name = odin.StringField()
    num_pages = odin.IntegerField()
    price = odin.FloatField()
    genre = odin.StringField(choices=(
        ('sci-fi', 'Science Fiction'),
        ('fantasy', 'Fantasy'),
        ('biography', 'Biography'),
        ('others', 'Others'),
    ))
    published = odin.DateTimeField()
    author = odin.ObjectAs(Author)
    publisher = odin.ObjectAs(Publisher)


class OldBookToBookMapping(odin.Mapping):
    from_resource = OldBook
    to_resource = Book

    exclude_fields = ('')

    mappings = (
        ('name', None, 'title'),
    )


class FromResource(odin.Resource):
    # Auto matched
    title = odin.StringField()
    count = odin.StringField()
    # Excluded
    excluded1 = odin.FloatField()
    # Mappings
    from_field1 = odin.StringField()
    from_field2 = odin.StringField()
    from_field3 = odin.IntegerField()
    from_field4 = odin.IntegerField()
    # Custom mappings
    from_field_c1 = odin.StringField()
    from_field_c2 = odin.StringField()
    from_field_c3 = odin.StringField()
    from_field_c4 = odin.StringField()
    not_auto_c5 = odin.StringField()


class ToResource(odin.Resource):
    # Auto matched
    title = odin.StringField()
    count = odin.IntegerField()
    # Excluded
    excluded1 = odin.FloatField()
    # Mappings
    to_field1 = odin.StringField()
    to_field2 = odin.IntegerField()
    to_field3 = odin.IntegerField()
    # Custom mappings
    to_field_c1 = odin.StringField()
    to_field_c2 = odin.StringField()
    to_field_c3 = odin.StringField()
    not_auto_c5 = odin.StringField()



class FromToMapping(odin.Mapping):
    from_resource = FromResource
    to_resource = ToResource

    exclude_fields = ('excluded1',)

    mappings = (
        ('from_field1', None, 'to_field1'),
        ('from_field2', int, 'to_field2'),
        (('from_field3', 'from_field4'), sum_fields, 'to_field3'),
    )

    @odin.map_field(('from_field_c1', 'from_field_c2', 'from_field_c3'), 'to_field_c1')
    def multi_to_one(self, *fields):
        return '-'.join(fields)

    @odin.map_field('from_field_c4', ('to_field_c2', 'to_field_c3'))
    def one_to_multi(self, field):
        return tuple(field.split('-', 1))

    @odin.map_field('not_auto_c5')
    def _not_auto_c5(self, field):
        return field.upper()
