# -*- coding: utf-8 -*-
import unittest
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


class ResourceTestCase(unittest.TestCase):
    def test_constructor_1(self):
        r = Author(name="Foo")
        self.assertEqual("Foo", r.name)

    def test_constructor_2(self):
        with self.assertRaises(TypeError):
            Author(name="Foo", age=42)

    def test_simple_methods(self):
        r = Author()
        self.assertEqual("<Author: test_resources.Author resource>", repr(r))
        self.assertEqual("test_resources.Author resource", str(r))

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