# -*- coding: utf-8 -*-
import unittest
from odin import utils
from .resources import Book


class TestCamelAndDashFormats(object):
    def test_camel_to_lower_separated(self):
        assert "this_is_an_example" == utils.camel_to_lower_underscore('thisIsAnExample')
        assert "this_is_an_example" == utils.camel_to_lower_underscore('ThisIsAnExample')
        assert "this-is-a-test" == utils.camel_to_lower_dash('thisIsATest')

    def test_lower_underscore_to_camel(self):
        assert "thisIsAnExample" == utils.lower_underscore_to_camel('this_is_an_example')
        assert "thisIsAnExample" == utils.lower_underscore_to_camel('this_is_an_example')
        assert "thisIsATest" == utils.lower_underscore_to_camel('this_Is_A_test')

    def test_lower_dash_to_camel(self):
        assert "thisIsAnExample" == utils.lower_dash_to_camel('this-is-an-example')
        assert "thisIsAnExample" == utils.lower_dash_to_camel('this-is-an-example')
        assert "thisIsATest" == utils.lower_dash_to_camel('this-Is-A-test')


class TestIterator(object):
    def test_extract_fields_from_dict(self):
        source_dict = {
            'title': "My Title",
            'num_pages': 1,
            'rrp': 1.2,
            'fiction': True,
            'published': ['no_validation_for_type'],
            'another_field': 'that is not on the resource'
        }

        assert {
            'title': "My Title",
            'num_pages': 1,
            'rrp': 1.2,
            'fiction': True,
            'published': ['no_validation_for_type'],
        } == utils.extract_fields_from_dict(source_dict, Book)


class TestValueInChoice(object):
    CHOICES = (
        ('foo', 'Foo'),
        ('bar', 'Foo'),
        (123, 'Number'),
        (True, 'Boolean'),
        (None, 'None'),
        ('eek', 'With Help', 'Help string'),
    )

    def test_value_in_choices(self):
        assert utils.value_in_choices('foo', self.CHOICES)
        assert utils.value_in_choices(123, self.CHOICES)
        assert utils.value_in_choices(True, self.CHOICES)
        assert utils.value_in_choices(None, self.CHOICES)
        assert utils.value_in_choices('eek', self.CHOICES)
        assert not utils.value_in_choices('xyz', self.CHOICES)
        assert not utils.value_in_choices(False, self.CHOICES)
        assert not utils.value_in_choices(321, self.CHOICES)
