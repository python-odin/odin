# -*- coding: utf-8 -*-
import unittest
from odin.contrib.pint import units, FloatQField
from odin.contrib.pint.units import registry
from odin.exceptions import ValidationError


class PintFieldsTestCase(unittest.TestCase):
    def test_floatq_field_init(self):
        self.assertRaises(ValueError, FloatQField, None)

    def test_floatqfield_1(self):
        f = FloatQField('kWh')
        self.assertRaises(ValidationError, f.clean, None)
        self.assertRaises(ValidationError, f.clean, 10.2 * registry.meter)
        self.assertRaises(ValidationError, f.clean, 'abc')
        self.assertEqual(10.2 * registry.kilowatt_hour, f.clean(10.2 * registry.kilowatt_hour))
        self.assertEqual(10.2 * registry['kWh'], f.clean(10.2))
        self.assertEqual(10.2 * registry['kWh'], f.clean((10.2, 'kWh')))
        self.assertEqual(10.2 * registry['kWh'], f.clean((10.2, registry.kilowatt_hour)))
        self.assertEqual(10.2 * registry.watt_hour, f.clean(10.2 * registry.watt_hour))
