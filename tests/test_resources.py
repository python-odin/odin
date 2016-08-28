# -*- coding: utf-8 -*-
from __future__ import absolute_import
import pytest
import odin
from odin.fields import NOT_PROVIDED
from odin.resources import ResourceOptions, build_object_graph
from odin.exceptions import ValidationError
from .resources import Book, Library, Subscriber


class Author(odin.Resource):
    name = odin.StringField()
    country = odin.StringField(null=True)

    def clean(self):
        if self.name == "Bruce" and self.country.startswith("Australia"):
            raise ValidationError("No no no no")

    def clean_country(self, value):
        if value not in ["Australia", "New Zealand"]:
            raise ValidationError("What are ya?")
        return "%s!" % value

    def extra_attrs(self, attrs):
        self.extras = attrs


# Resources for abstract namespace test.
class ResourceA(odin.Resource):
    class Meta:
        abstract = True
        namespace = "example"


class ResourceB(ResourceA):
    class Meta:
        abstract = True


class ResourceC(ResourceB):
    pass


class ResourceD(ResourceC):
    pass


class TestResource(object):
    def test_constructor_kwargs_only(self):
        r = Author(name="Foo")
        assert "Foo" == r.name

    def test_constructor_kwargs_only_with_unknown_field(self):
        with pytest.raises(TypeError):
            Author(name="Foo", age=42)

    def test_constructor_args_only(self):
        r = Author("Foo")
        assert "Foo" == r.name
        assert None == r.country

    def test_constructor_args_excess(self):
        with pytest.raises(TypeError) as ex:
            Author("Foo", "Australia", 42)
        assert "This resource takes 2 positional arguments but 3 where given." == str(ex.value)

    def test_constructor_args_and_kwargs(self):
        r = Author("Foo", country="Australia")
        assert "Foo" == r.name
        assert "Australia" == r.country

    def test_constructor_args_and_kwargs_overrides(self):
        r = Author("Foo", name="Bar", country="Australia")
        assert "Foo" == r.name
        assert "Australia" == r.country

    def test_simple_methods(self):
        r = Author()
        assert "<Author: tests.test_resources.Author resource>" == repr(r)
        assert "tests.test_resources.Author resource" == str(r)

    def test_clean_fields_1(self):
        r = Author(name="Foo")
        r.country = "Australia"

        r.clean_fields()

        assert "Foo" == r.name
        assert "Australia!" == r.country

    def test_clean_fields_2(self):
        r = Author(name="Foo")

        r.clean_fields()

        assert "Foo" == r.name
        assert None == r.country

    def test_clean_fields_3(self):
        r = Author(name="Foo", country="England")

        try:
            r.clean_fields()
        except ValidationError as ve:
            assert ["What are ya?"] == ve.message_dict['country']
        else:
            raise AssertionError("ValidationError not raised.")

    def test_clean_fields_4(self):
        r = Author()

        try:
            r.clean_fields()
        except ValidationError as ve:
            assert ["This field cannot be null."] == ve.message_dict['name']
        else:
            raise AssertionError("ValidationError not raised.")

    def test_full_clean(self):
        r = Author(name="Bruce", country="Australia")

        try:
            r.full_clean()
        except ValidationError as ve:
            assert ["No no no no"] == ve.message_dict['__all__']
        else:
            raise AssertionError("ValidationError not raised.")

    def test_full_clean_exclude(self):
        r = Author(name="Bruce", country="England")

        r.full_clean(exclude=('country',))

        assert "Bruce" == r.name
        assert "England" == r.country

    # Fix for #11
    def test_multiple_abstract_namespaces(self):
        assert 'example.ResourceC' == ResourceC._meta.resource_name

    def test_parents_1(self):
        assert [] == ResourceA._meta.parents
        assert [ResourceA] == ResourceB._meta.parents
        assert [ResourceA, ResourceB] == ResourceC._meta.parents
        assert [ResourceA, ResourceB, ResourceC] == ResourceD._meta.parents


class TestMetaOptions(object):
    def test_invalid_options(self):
        class Meta:
            random_val = 10

        class NewResource(object):
            pass

        target = ResourceOptions(Meta)

        with pytest.raises(TypeError):
            target.contribute_to_class(NewResource, 'etc')


class TestConstructionMethods(object):
    def test_build_object_graph_empty_dict_no_clean(self):
        book = build_object_graph({}, Book, full_clean=False)

        assert dict(
            title=None,
            isbn=None,
            num_pages=None,
            rrp=20.4,
            fiction=None,
            genre=None,
            published=None,
            authors=None,
            publisher=None
        ) == book.to_dict()

    def test_build_object_graph_empty_dict(self):
        with pytest.raises(ValidationError) as ctx:
            build_object_graph({}, Book)

        assert dict(
            title=['This field cannot be null.'],
            isbn=['This field cannot be null.'],
            num_pages=['This field cannot be null.'],
            fiction=['This field cannot be null.'],
            genre=['This field cannot be null.'],
            published=['This field cannot be null.'],
            authors=['List cannot contain null entries.'],
        ) == ctx.value.error_messages

    def test_build_object_graph_from_list(self):
        books = build_object_graph([dict(
            title="Book1"
        ), dict(
            title="Book2"
        )], Book, full_clean=False)

        assert [dict(
            title="Book1",
            isbn=None,
            num_pages=None,
            rrp=20.4,
            fiction=None,
            genre=None,
            published=None,
            authors=None,
            publisher=None
        ), dict(
            title="Book2",
            isbn=None,
            num_pages=None,
            rrp=20.4,
            fiction=None,
            genre=None,
            published=None,
            authors=None,
            publisher=None
        )] == [book.to_dict() for book in books]

    def test_build_nested_objects(self):
        subscribers = [
            {'name': 'John Smith', 'address': 'Oak Lane 1234'},
            {'name': 'Johnny Smith', 'address': 'Oak Lane 1235'}]

        library = {
            'name': 'John Smith Library',
            'subscribers': subscribers
        }

        expected = sorted(build_object_graph(subscribers, resource=Subscriber, full_clean=False), key=lambda s: s.name)
        actual = sorted(build_object_graph(library, resource=Library, full_clean=False).subscribers, key=lambda s: s.name)

        assert actual == expected

    def test_build_nested_objects_with_polymorphism(self):
        books = [{'title': "Book1", "isbn": "abc-123", 'num_pages': 1, 'rrp': 20.4, 'fiction': True, 'genre': 'sci-fi', 'published': [],
                  'authors': [], 'publisher': None, '$': 'tests.resources.Book'},
                 {'title': "Book2", "isbn": "def-456", 'num_pages': 1, 'rrp': 20.4, 'fiction': True, 'genre': 'sci-fi', 'published': [],
                  'authors': [], 'publisher': None, '$': 'tests.resources.Book'}]

        library = {
            'name': 'John Smith Library',
            'books': books
        }

        expected = sorted(build_object_graph(books, full_clean=False), key=lambda s: s.title)
        actual = sorted(build_object_graph(library, resource=Library, full_clean=False).books, key=lambda s: s.title)

        assert actual == expected

    def test_create_resource_from_dict_with_default_to_not_supplied(self):
        book = build_object_graph({
            "title": "Foo",
            "num_pages": 42
        }, Book, full_clean=False, default_to_not_supplied=True)

        assert dict(
            title="Foo",
            isbn=NOT_PROVIDED,
            num_pages=42,
            rrp=NOT_PROVIDED,
            fiction=NOT_PROVIDED,
            genre=NOT_PROVIDED,
            published=NOT_PROVIDED,
            authors=NOT_PROVIDED,
            publisher=NOT_PROVIDED
        ) == book.to_dict()
