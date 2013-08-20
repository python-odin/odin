# -*- coding: utf-8 -*-
import unittest
from odin import utils


class CamelAndDashFormatsTestCase(unittest.TestCase):
    def test_camel_to_lower_separated(self):
        self.assertEqual("this_is_an_example", utils.camel_to_lower_underscore('thisIsAnExample'))
        self.assertEqual("this_is_an_example", utils.camel_to_lower_underscore('ThisIsAnExample'))
        self.assertEqual("this-is-a-test", utils.camel_to_lower_dash('thisIsATest'))

    def test_lower_underscore_to_camel(self):
        self.assertEqual("thisIsAnExample", utils.lower_underscore_to_camel('this_is_an_example'))
        self.assertEqual("thisIsAnExample", utils.lower_underscore_to_camel('this_is_an_example'))
        self.assertEqual("thisIsATest", utils.lower_underscore_to_camel('this_Is_A_test'))

    def test_lower_dash_to_camel(self):
        self.assertEqual("thisIsAnExample", utils.lower_dash_to_camel('this-is-an-example'))
        self.assertEqual("thisIsAnExample", utils.lower_dash_to_camel('this-is-an-example'))
        self.assertEqual("thisIsATest", utils.lower_dash_to_camel('this-Is-A-test'))