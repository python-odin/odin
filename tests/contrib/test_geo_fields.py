# -*- coding: utf-8 -*-
import unittest
from odin.contrib.geo.datatypes import latitude, longitude, latlng, point
from odin.contrib.geo.fields import LatitudeField, LongitudeField, LatLngField, PointField
from odin.exceptions import ValidationError


class GeoFieldsTestCase(unittest.TestCase):
    # LatitudeField ###########################################################

    def test_latitude_field(self):
        f = LatitudeField()
        self.assertRaises(ValidationError, f.clean, None)
        self.assertRaises(ValidationError, f.clean, 'a')
        self.assertRaises(ValidationError, f.clean, 92)
        self.assertRaises(ValidationError, f.clean, -92)
        self.assertEqual(12.345, f.clean(12.345))
        self.assertEqual(-12.345, f.clean(-12.345))
        self.assertEqual(12.345, f.clean('12.345'))
        self.assertIsInstance(f.clean(12.345), latitude)

    # LongitudeField ##########################################################

    def test_longitude_field(self):
        f = LongitudeField()
        self.assertRaises(ValidationError, f.clean, None)
        self.assertRaises(ValidationError, f.clean, 'a')
        self.assertRaises(ValidationError, f.clean, 182)
        self.assertRaises(ValidationError, f.clean, -182)
        self.assertEqual(123.456, f.clean(123.456))
        self.assertEqual(-123.456, f.clean(-123.456))
        self.assertEqual(123.456, f.clean('123.456'))
        self.assertIsInstance(f.clean(122.456), longitude)

    # LatLngField #############################################################

    def test_latlng_field(self):
        f = LatLngField()
        self.assertRaises(ValidationError, f.clean, None)
        self.assertRaises(ValidationError, f.clean, 'a')
        self.assertRaises(ValidationError, f.clean, [])
        self.assertRaises(ValidationError, f.clean, [12.345])
        self.assertRaises(ValidationError, f.clean, [92, 123.345])
        self.assertRaises(ValidationError, f.clean, [12.345, 182])

        self.assertEqual((12.345, 123.456), f.clean((12.345, 123.456)))
        self.assertEqual((12.345, 123.456), f.clean(('12.345', '123.456')))
        self.assertIsInstance(f.clean((12.345, 123.456)), latlng)

    # PointField ##############################################################

    def test_point_field(self):
        f = PointField()
        self.assertRaises(ValidationError, f.clean, None)
        self.assertRaises(ValidationError, f.clean, 'a')
        self.assertRaises(ValidationError, f.clean, [])
        self.assertRaises(ValidationError, f.clean, [1])
        self.assertRaises(ValidationError, f.clean, [1, 2, 3, 4])
        self.assertRaises(ValidationError, f.clean, [1, 2, 'a', 4])

        self.assertEqual((1, 2), f.clean((1, 2)))
        self.assertEqual((1, 2), f.clean(('1', '2')))
        self.assertEqual((1, 2, 3), f.clean((1, 2, 3)))
        self.assertEqual((1, 2, 3), f.clean(('1', '2', '3')))
        self.assertIsInstance(f.clean((1, 2)), point)
        self.assertIsInstance(f.clean((1, 2, 3)), point)
