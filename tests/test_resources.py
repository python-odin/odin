import pytest

import odin
from odin.exceptions import ResourceDefError, ValidationError
from odin.fields import NotProvided
from odin.resources import (
    Resource,
    ResourceOptions,
    build_object_graph,
    create_resource_from_dict,
)
from odin.utils import getmeta, snake_to_camel

from .resources import (
    Book,
    BookProxy,
    InheritedCamelCaseResource,
    Library,
    Subscriber,
    AltBook,
    LibraryBook
)


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

    a = odin.StringField()


class ResourceB(ResourceA):
    class Meta:
        abstract = True

    b = odin.StringField()


class ResourceC(ResourceB):
    c = odin.StringField()


class ResourceD(ResourceC):
    class Meta:
        field_sorting = True

    d = odin.StringField()


class ResourceE(ResourceD):
    class Meta:
        def field_sorting(fields):
            return sorted(fields, key=lambda f: f.name)

    aa = odin.StringField()


class ResourceF(ResourceE):
    aaa = odin.StringField()


class ResourceG(odin.Resource):
    """
    Test with user metadata
    """

    class Meta:
        user_data = {"custom": "my-custom-metadata"}

    name = odin.StringField()


class TestResource:
    def test_constructor_kwargs_only(self):
        r = Author(name="Foo")
        assert "Foo" == r.name

    def test_constructor_kwargs_only_with_unknown_field(self):
        with pytest.raises(TypeError):
            Author(name="Foo", age=42)

    def test_constructor_args_only(self):
        r = Author("Foo")
        assert r.name == "Foo"
        assert r.country is None

    def test_constructor_args_excess(self):
        with pytest.raises(TypeError) as ex:
            Author("Foo", "Australia", 42)
        assert "This resource takes 2 positional arguments but 3 where given." == str(
            ex.value
        )

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
        assert r.country is None

    def test_clean_fields_3(self):
        r = Author(name="Foo", country="England")

        try:
            r.clean_fields()
        except ValidationError as ve:
            assert ["What are ya?"] == ve.message_dict["country"]
        else:
            raise AssertionError("ValidationError not raised.")

    def test_clean_fields_4(self):
        r = Author()

        try:
            r.clean_fields()
        except ValidationError as ve:
            assert ["This field cannot be null."] == ve.message_dict["name"]
        else:
            raise AssertionError("ValidationError not raised.")

    def test_full_clean(self):
        r = Author(name="Bruce", country="Australia")

        try:
            r.full_clean()
        except ValidationError as ve:
            assert ["No no no no"] == ve.message_dict["__all__"]
        else:
            raise AssertionError("ValidationError not raised.")

    def test_full_clean_exclude(self):
        r = Author(name="Bruce", country="England")

        r.full_clean(exclude=("country",))

        assert "Bruce" == r.name
        assert "England" == r.country

    # Fix for #11
    def test_multiple_abstract_namespaces(self):
        assert "example.ResourceC" == ResourceC._meta.resource_name

    def test_parents_1(self):
        assert [] == ResourceA._meta.parents
        assert [ResourceA] == ResourceB._meta.parents
        assert [ResourceA, ResourceB] == ResourceC._meta.parents
        assert [ResourceA, ResourceB, ResourceC] == ResourceD._meta.parents

    def test_field_sorting(self):
        assert ["c", "b", "a"] == [f.name for f in ResourceC._meta.fields]

    def test_field_sorting__enabled(self):
        assert ["a", "b", "c", "d"] == [f.name for f in ResourceD._meta.fields]

    def test_field_sorting__callable(self):
        assert ["a", "aa", "b", "c", "d"] == [f.name for f in ResourceE._meta.fields]

    def test_field_sorting__inherited(self):
        assert ["a", "aa", "aaa", "b", "c", "d"] == [
            f.name for f in ResourceF._meta.fields
        ]

    def test_user_data__where_not_supplied(self):
        assert getmeta(ResourceA).user_data is None

    def test_user_data__where_supplied_on_type(self):
        assert getmeta(ResourceG).user_data == {"custom": "my-custom-metadata"}

    def test_user_data__where_supplied_on_instance(self):
        target = ResourceG(name="Ludwig")
        assert getmeta(target).user_data == {"custom": "my-custom-metadata"}


class TestMetaOptions:
    def test_invalid_options(self):
        class Meta:
            random_val = 10

        class NewResource:
            pass

        target = ResourceOptions(Meta)

        with pytest.raises(TypeError):
            target.contribute_to_class(NewResource, "etc")

    def test_use_a_reserved_field(self):
        with pytest.raises(ResourceDefError, match="fields"):

            class InvalidFieldsResource(Resource):
                fields = odin.StringField()

    def test_shadow_fields_are_identified(self):
        target = getmeta(AltBook)

        actual = target.shadow_fields

        assert isinstance(actual, tuple)
        assert [f.name for f in actual] == ["title"]

    def test_abstract_option_is_set_for_abstract_resources(self):
        target = getmeta(LibraryBook)

        actual = target.abstract

        assert actual is True

    def test_abstract_option_is_clear_for_non_abstract_resources(self):
        target = getmeta(Book)

        actual = target.abstract

        assert actual is False

class TestConstructionMethods:
    def test_build_object_graph_empty_dict_no_clean(self):
        book = build_object_graph({}, Book, full_clean=False)

        assert {
            "title": None,
            "isbn": None,
            "num_pages": None,
            "rrp": 20.4,
            "fiction": None,
            "genre": None,
            "published": None,
            "authors": None,
            "publisher": None,
        } == book.to_dict()

    def test_build_object_graph_empty_dict(self):
        with pytest.raises(ValidationError) as ctx:
            build_object_graph({}, Book)

        assert {
            "title": ["This field cannot be null."],
            "isbn": ["This field cannot be null."],
            "num_pages": ["This field cannot be null."],
            "fiction": ["This field cannot be null."],
            "genre": ["This field cannot be null."],
            "published": ["This field cannot be null."],
            "authors": ["List cannot contain null entries."],
        } == ctx.value.error_messages

    def test_build_object_graph_from_list(self):
        books = build_object_graph(
            [{"title": "Book1"}, {"title": "Book2"}], Book, full_clean=False
        )

        assert [
            {
                "title": "Book1",
                "isbn": None,
                "num_pages": None,
                "rrp": 20.4,
                "fiction": None,
                "genre": None,
                "published": None,
                "authors": None,
                "publisher": None,
            },
            {
                "title": "Book2",
                "isbn": None,
                "num_pages": None,
                "rrp": 20.4,
                "fiction": None,
                "genre": None,
                "published": None,
                "authors": None,
                "publisher": None,
            },
        ] == [book.to_dict() for book in books]

    def test_build_nested_objects(self):
        subscribers = [
            {"name": "John Smith", "address": "Oak Lane 1234"},
            {"name": "Johnny Smith", "address": "Oak Lane 1235"},
        ]

        library = {"name": "John Smith Library", "subscribers": subscribers}

        expected = sorted(
            build_object_graph(subscribers, resource=Subscriber, full_clean=False),
            key=lambda s: s.name,
        )
        actual = sorted(
            build_object_graph(library, resource=Library, full_clean=False).subscribers,
            key=lambda s: s.name,
        )

        assert actual == expected

    def test_build_nested_objects_with_polymorphism(self):
        books = [
            {
                "title": "Book1",
                "isbn": "abc-123",
                "num_pages": 1,
                "rrp": 20.4,
                "fiction": True,
                "genre": "sci-fi",
                "published": [],
                "authors": [],
                "publisher": None,
                "$": "tests.resources.Book",
            },
            {
                "title": "Book2",
                "isbn": "def-456",
                "num_pages": 1,
                "rrp": 20.4,
                "fiction": True,
                "genre": "sci-fi",
                "published": [],
                "authors": [],
                "publisher": None,
                "$": "tests.resources.Book",
            },
        ]

        library = {"name": "John Smith Library", "books": books}

        expected = sorted(
            build_object_graph(books, full_clean=False), key=lambda s: s.title
        )
        actual = sorted(
            build_object_graph(library, resource=Library, full_clean=False).books,
            key=lambda s: s.title,
        )

        assert actual == expected

    def test_create_resource_from_dict_with_default_to_not_supplied(self):
        book = create_resource_from_dict(
            {"title": "Foo", "num_pages": 42},
            Book,
            full_clean=False,
            default_to_not_provided=True,
        )

        assert {
            "title": "Foo",
            "isbn": NotProvided,
            "num_pages": 42,
            "rrp": NotProvided,
            "fiction": NotProvided,
            "genre": NotProvided,
            "published": NotProvided,
            "authors": NotProvided,
            "publisher": NotProvided,
        } == book.to_dict()

    def test_create_resource_from_dict__with_proxy(self):
        book = create_resource_from_dict(
            {"title": "Foo", "num_pages": 42, "rrp": 10000.99, "fiction": True},
            BookProxy,
            full_clean=False,
            default_to_not_provided=True,
        )

        assert {
            "title": "Foo",
            "isbn": NotProvided,
            "num_pages": 42,
            "rrp": 20.4,
        } == book.to_dict()

    def test_inheritance_of_meta_options(self):
        options = getmeta(InheritedCamelCaseResource)

        assert options.resource_name == "foo.bar.InheritedCamelCaseResource"
        assert options.field_name_format is snake_to_camel

    def test_field_name_format(self):
        options = getmeta(InheritedCamelCaseResource)

        actual = [field.name for field in options.fields]

        assert actual == ["fullName", "yearOfBirth", "emailAddress"]

    def test_shadowing(self):
        actual = AltBook(title="Foo", isbn="123456")

        getmeta(actual)

        book = Book(title="Foo", isbn="123456")

        assert book.isbn == "123456"
        assert book.title == "Foo"
