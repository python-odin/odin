# -*- coding: utf-8 -*-
import unittest
from odin.resources import ResourceOptions
import odin
from odin.exceptions import ValidationError


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


class ResourceTestCase(unittest.TestCase):
    def test_constructor_kwargs_only(self):
        r = Author(name="Foo")
        self.assertEqual("Foo", r.name)

    def test_constructor_kwargs_only_with_unknown_field(self):
        with self.assertRaises(TypeError):
            Author(name="Foo", age=42)

    def test_constructor_args_only(self):
        r = Author("Foo")
        self.assertEqual("Foo", r.name)
        self.assertEqual(None, r.country)

    def test_constructor_args_excess(self):
        with self.assertRaises(TypeError) as ex:
            Author("Foo", "Australia", 42)
        self.assertEqual("This resource takes 2 positional arguments but 3 where given.", str(ex.exception))

    def test_constructor_args_and_kwargs(self):
        r = Author("Foo", country="Australia")
        self.assertEqual("Foo", r.name)
        self.assertEqual("Australia", r.country)

    def test_constructor_args_and_kwargs_overrides(self):
        r = Author("Foo", name="Bar", country="Australia")
        self.assertEqual("Foo", r.name)
        self.assertEqual("Australia", r.country)

    def test_simple_methods(self):
        r = Author()
        self.assertEqual("<Author: tests.test_resources.Author resource>", repr(r))
        self.assertEqual("tests.test_resources.Author resource", str(r))

    def test_clean_fields_1(self):
        r = Author(name="Foo")
        r.country = "Australia"

        r.clean_fields()

        self.assertEqual("Foo", r.name)
        self.assertEqual("Australia!", r.country)

    def test_clean_fields_2(self):
        r = Author(name="Foo")

        r.clean_fields()

        self.assertEqual("Foo", r.name)
        self.assertEqual(None, r.country)

    def test_clean_fields_3(self):
        r = Author(name="Foo", country="England")

        try:
            r.clean_fields()
        except ValidationError as ve:
            self.assertEqual(["What are ya?"], ve.message_dict['country'])
        else:
            raise AssertionError("ValidationError not raised.")

    def test_clean_fields_4(self):
        r = Author()

        try:
            r.clean_fields()
        except ValidationError as ve:
            self.assertEqual(["This field cannot be null."], ve.message_dict['name'])
        else:
            raise AssertionError("ValidationError not raised.")

    def test_full_clean(self):
        r = Author(name="Bruce", country="Australia")

        try:
            r.full_clean()
        except ValidationError as ve:
            self.assertEqual(["No no no no"], ve.message_dict['__all__'])
        else:
            raise AssertionError("ValidationError not raised.")

    # Fix for #11
    def test_multiple_abstract_namespaces(self):
        self.assertEqual('example.ResourceC', ResourceC._meta.resource_name)

    def test_parents_1(self):
        self.assertListEqual([], ResourceA._meta.parents)
        self.assertListEqual([ResourceA], ResourceB._meta.parents)
        self.assertListEqual([ResourceA, ResourceB], ResourceC._meta.parents)
        self.assertListEqual([ResourceA, ResourceB, ResourceC], ResourceD._meta.parents)


class MetaOptionsTestCase(unittest.TestCase):
    def test_invalid_options(self):
        class Meta:
            random_val = 10

        class NewResource(object):
            pass

        target = ResourceOptions(Meta)

        with self.assertRaises(TypeError):
            target.contribute_to_class(NewResource, 'etc')
