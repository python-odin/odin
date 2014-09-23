# -*- coding: utf-8 -*-
import unittest
import six
from odin.contrib.geo import datatypes


class DataTypesTestCase(unittest.TestCase):
    def test_to_dms(self):
        # I am aware that round in python is not accurate but in this case I have calculated the test values
        # specifically so that the rounding will not effect the outcome of this test.
        d, m, s = datatypes.to_dms(27.3375)
        self.assertEqual((27, 20, 15), (d, m, round(s, 5)))

        d, m, s = datatypes.to_dms(-27.3375)
        self.assertEqual((-27, 20, 15), (d, m, round(s, 5)))

        d, m, s = datatypes.to_dms(-27.3375, True)
        self.assertEqual((27, 20, 15), (d, m, round(s, 5)))

    def test_to_dm(self):
        # I am aware that round in python is not accurate but in this case I have calculated the test values
        # specifically so that the rounding will not effect the outcome of this test.
        d, m = datatypes.to_dm(27.3375)
        self.assertEqual((27, 20.25), (d, round(m, 5)))

        d, m = datatypes.to_dm(-27.3375)
        self.assertEqual((-27, 20.25), (d, round(m, 5)))

        d, m = datatypes.to_dm(-27.3375, True)
        self.assertEqual((27, 20.25), (d, round(m, 5)))

    def test_latitude_valid(self):
        self.assertEqual(30, datatypes.latitude(30))
        self.assertEqual(-30, datatypes.latitude(-30))
        self.assertEqual(90.0, datatypes.latitude(90.0))
        self.assertEqual(-90.0, datatypes.latitude(-90.0))
        self.assertEqual(42.0, datatypes.latitude("42.0"))
        self.assertEqual(-42.0, datatypes.latitude("-42.0"))
        self.assertEqual(42.0, datatypes.latitude(float(42.0)))
        self.assertEqual(-42.0, datatypes.latitude(float(-42.0)))
        self.assertEqual(42.0, datatypes.latitude(datatypes.latitude(42.0)))
        self.assertEqual(-42.0, datatypes.latitude(datatypes.latitude(-42.0)))

    def test_latitude_invalid(self):
        self.assertRaises(TypeError, datatypes.latitude, None)
        self.assertRaises(ValueError, datatypes.latitude, 'a')
        self.assertRaises(ValueError, datatypes.latitude, 92.0)
        self.assertRaises(ValueError, datatypes.latitude, -92.0)
        self.assertRaises(TypeError, datatypes.latitude, 1, 2)

    def test_latitude_str(self):
        lat = datatypes.latitude(27.3375)
        self.assertEqual("27.3375", repr(lat))
        self.assertEqual(u"27°20'15.000000\"N", six.text_type(lat))

        lat = datatypes.latitude(-27.3375)
        self.assertEqual("-27.3375", repr(lat))
        self.assertEqual(u"27°20'15.000000\"S", six.text_type(lat))

    def test_longitude_valid(self):
        self.assertEqual(30, datatypes.longitude(30))
        self.assertEqual(-30, datatypes.longitude(-30))
        self.assertEqual(180.0, datatypes.longitude(180.0))
        self.assertEqual(-180.0, datatypes.longitude(-180.0))
        self.assertEqual(42.0, datatypes.longitude("42.0"))
        self.assertEqual(-42.0, datatypes.longitude("-42.0"))
        self.assertEqual(42.0, datatypes.longitude(float(42.0)))
        self.assertEqual(-42.0, datatypes.longitude(float(-42.0)))
        self.assertEqual(42.0, datatypes.longitude(datatypes.longitude(42.0)))
        self.assertEqual(-42.0, datatypes.longitude(datatypes.longitude(-42.0)))

    def test_longitude_invalid(self):
        self.assertRaises(TypeError, datatypes.longitude, None)
        self.assertRaises(ValueError, datatypes.longitude, 'a')
        self.assertRaises(ValueError, datatypes.longitude, 182.0)
        self.assertRaises(ValueError, datatypes.longitude, -182.0)
        self.assertRaises(TypeError, datatypes.longitude, 1, 2)

    def test_longitude_str(self):
        lat = datatypes.longitude(27.3375)
        self.assertEqual("27.3375", repr(lat))
        self.assertEqual(u"027°20'15.000000\"E", six.text_type(lat))

        lat = datatypes.longitude(-27.3375)
        self.assertEqual("-27.3375", repr(lat))
        self.assertEqual(u"027°20'15.000000\"W", six.text_type(lat))

    def test_latlng_valid(self):
        self.assertEqual((10.0, 20.0), datatypes.latlng(10, 20))
        self.assertEqual((10.0, 20.0), datatypes.latlng('10', '20'))
        self.assertEqual((10.0, 20.0), datatypes.latlng(datatypes.latitude(10), datatypes.longitude(20)))
        self.assertEqual((10.0, 20.0), datatypes.latlng((10, 20)))
        self.assertEqual((90.0, 180.0), datatypes.latlng(90, 180))
        self.assertEqual((-90.0, -180.0), datatypes.latlng(-90, -180))

    def test_latlng_invalid(self):
        self.assertRaises(TypeError, datatypes.latlng, None)
        self.assertRaises(TypeError, datatypes.latlng, 1)
        self.assertRaises(TypeError, datatypes.latlng, 1, 2, 3)
        self.assertRaises(TypeError, datatypes.latlng, (1, 2, 3))
        self.assertRaises(ValueError, datatypes.latlng, 90, 'a')
        self.assertRaises(ValueError, datatypes.latlng, 100, 100)

    def test_latlng_str(self):
        ll = datatypes.latlng(27.3375, -27.3375)
        self.assertEqual("latlng<27.3375, -27.3375>", repr(ll))
        self.assertEqual(u"(27°20'15.000000\"N, 027°20'15.000000\"W)", six.text_type(ll))

    def test_latlng_properties(self):
        ll = datatypes.latlng(27.3375, -27.3375)
        self.assertEqual(27.3375, ll.lat)
        self.assertEqual(-27.3375, ll.lng)

    def test_point_valid(self):
        self.assertEqual((1, 2), datatypes.point(1, 2))
        self.assertEqual((1, 2), datatypes.point('1', '2'))
        self.assertEqual((1, 2), datatypes.point((1, 2)))
        self.assertEqual((1, 2, 3), datatypes.point(1, 2, 3))
        self.assertEqual((1, 2, 3), datatypes.point('1', '2', '3'))
        self.assertEqual((1, 2, 3), datatypes.point((1, 2, 3)))

    def test_point_invalid(self):
        self.assertRaises(TypeError, datatypes.point, None)
        self.assertRaises(TypeError, datatypes.point, 1)
        self.assertRaises(TypeError, datatypes.point, 1, 2, 3, 4)
        self.assertRaises(TypeError, datatypes.point, (1, 2, 3, 4))
        self.assertRaises(ValueError, datatypes.point, 90, 'a', 1)

    def test_point_str(self):
        p = datatypes.point(1, 2)
        self.assertEqual("point<1.000000, 2.000000>", repr(p))
        self.assertEqual("(1.000000, 2.000000)", str(p))

        p = datatypes.point(1, 2, 3)
        self.assertEqual("point<1.000000, 2.000000, 3.000000>", repr(p))
        self.assertEqual("(1.000000, 2.000000, 3.000000)", str(p))

    def test_point_properties(self):
        p = datatypes.point(1, 2)
        self.assertEqual(1, p.x)
        self.assertEqual(2, p.y)
        self.assertRaises(AttributeError, lambda: p.z)
        self.assertFalse(p.is_3d)

        p = datatypes.point(1, 2, 3)
        self.assertEqual(1, p.x)
        self.assertEqual(2, p.y)
        self.assertEqual(3, p.z)
        self.assertTrue(p.is_3d)
