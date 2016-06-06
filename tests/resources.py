# -*- coding: utf-8 -*-
import odin
from odin.fields.virtual import CalculatedField
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
    class Meta:
        key_field_name = 'isbn'

    title = odin.StringField()
    isbn = odin.StringField()
    num_pages = odin.IntegerField()
    rrp = odin.FloatField(default=20.4, use_default_if_not_provided=True)
    fiction = odin.BooleanField(is_attribute=True)
    genre = odin.StringField(choices=(
        ('sci-fi', 'Science Fiction'),
        ('fantasy', 'Fantasy'),
        ('biography', 'Biography'),
        ('others', 'Others'),
        ('computers-and-tech', 'Computers & technology'),
    ))
    published = odin.TypedArrayField(odin.DateTimeField())
    authors = odin.ArrayOf(Author, use_container=True)
    publisher = odin.DictAs(Publisher, null=True)

    def __eq__(self, other):
        if other:
            return vars(self) == vars(other)
        return False


class Subscriber(odin.Resource):
    name = odin.StringField()
    address = odin.StringField()

    def __eq__(self, other):
        if other:
            return self.name == other.name and self.address == other.address


class Library(odin.Resource):
    name = odin.StringField()
    books = odin.ArrayOf(LibraryBook)
    subscribers = odin.ArrayOf(Subscriber, null=True)
    book_count = CalculatedField(lambda o: len(o.books))

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
        ('computers-and-tech', 'Computers & technology'),
    ))
    published = odin.DateTimeField()
    author = odin.ObjectAs(Author)
    publisher = odin.ObjectAs(Publisher)


class OldBookToBookMapping(odin.Mapping):
    from_obj = OldBook
    to_obj = Book

    exclude_fields = ('',)

    mappings = (
        ('name', None, 'title'),
    )


class ChildResource(odin.Resource):
    name = odin.StringField()


class FromResource(odin.Resource):
    # Auto matched
    title = odin.StringField()
    count = odin.StringField()
    child = odin.ObjectAs(ChildResource)
    children = odin.ArrayOf(ChildResource)
    # Excluded
    excluded1 = odin.FloatField()
    # Mappings
    from_field1 = odin.StringField()
    from_field2 = odin.StringField()
    from_field3 = odin.IntegerField()
    from_field4 = odin.IntegerField()
    same_but_different = odin.StringField()
    # Custom mappings
    from_field_c1 = odin.StringField()
    from_field_c2 = odin.StringField()
    from_field_c3 = odin.StringField()
    from_field_c4 = odin.StringField()
    not_auto_c5 = odin.StringField()
    comma_separated_string = odin.StringField()
    # Virtual fields
    constant_field = odin.ConstantField(value=10)


class InheritedResource(FromResource):
    # Additional fields
    name = odin.StringField()
    # Additional virtual fields
    calculated_field = odin.CalculatedField(lambda obj: 11)


class MultiInheritedResource(InheritedResource, FromResource):
    pass


class ToResource(odin.Resource):
    # Auto matched
    title = odin.StringField()
    count = odin.IntegerField()
    child = odin.ObjectAs(ChildResource)
    children = odin.ArrayOf(ChildResource)
    # Excluded
    excluded1 = odin.FloatField()
    # Mappings
    to_field1 = odin.StringField()
    to_field2 = odin.IntegerField()
    to_field3 = odin.IntegerField()
    same_but_different = odin.StringField()
    # Custom mappings
    to_field_c1 = odin.StringField()
    to_field_c2 = odin.StringField()
    to_field_c3 = odin.StringField()
    not_auto_c5 = odin.StringField()
    array_string = odin.TypedArrayField(odin.StringField())
    assigned_field = odin.StringField()


class FromToMapping(odin.Mapping):
    from_obj = FromResource
    to_obj = ToResource

    exclude_fields = ('excluded1',)

    mappings = (
        ('from_field1', None, 'to_field1'),
        ('from_field2', int, 'to_field2'),
        (('from_field3', 'from_field4'), sum_fields, 'to_field3'),
        ('from_field1', None, 'same_but_different'),
    )

    @odin.map_field(from_field=('from_field_c1', 'from_field_c2', 'from_field_c3'), to_field='to_field_c1')
    def multi_to_one(self, *values):
        return '-'.join(values)

    @odin.map_field(from_field='from_field_c4', to_field=('to_field_c2', 'to_field_c3'))
    def one_to_multi(self, value):
        return value.split('-', 1)

    @odin.map_field
    def not_auto_c5(self, value):
        return value.upper()

    @odin.map_list_field(to_field='array_string')
    def comma_separated_string(self, value):
        return value.split(',')

    @odin.assign_field
    def assigned_field(self):
        return 'Foo'
