# -*- coding: utf-8 -*-
import pytest
import six
from odin.contrib.geo import datatypes


class TestDataTypes(object):
    def test_to_dms(self):
        # I am aware that round in python is not accurate but in this case I have calculated the test values
        # specifically so that the rounding will not effect the outcome of this test.
        d, m, s = datatypes.to_dms(27.3375)
        assert (27, 20, 15) == (d, m, round(s, 5))

        d, m, s = datatypes.to_dms(-27.3375)
        assert (-27, 20, 15) == (d, m, round(s, 5))

        d, m, s = datatypes.to_dms(-27.3375, True)
        assert (27, 20, 15) == (d, m, round(s, 5))

    def test_to_dm(self):
        # I am aware that round in python is not accurate but in this case I have calculated the test values
        # specifically so that the rounding will not effect the outcome of this test.
        d, m = datatypes.to_dm(27.3375)
        assert (27, 20.25) == (d, round(m, 5))

        d, m = datatypes.to_dm(-27.3375)
        assert (-27, 20.25) == (d, round(m, 5))

        d, m = datatypes.to_dm(-27.3375, True)
        assert (27, 20.25) == (d, round(m, 5))

    def test_latitude_valid(self):
        assert 30 == datatypes.latitude(30)
        assert -30 == datatypes.latitude(-30)
        assert 90.0 == datatypes.latitude(90.0)
        assert -90.0 == datatypes.latitude(-90.0)
        assert 42.0 == datatypes.latitude("42.0")
        assert -42.0 == datatypes.latitude("-42.0")
        assert 42.0 == datatypes.latitude(float(42.0))
        assert -42.0 == datatypes.latitude(float(-42.0))
        assert 42.0 == datatypes.latitude(datatypes.latitude(42.0))
        assert -42.0 == datatypes.latitude(datatypes.latitude(-42.0))

    def test_latitude_invalid(self):
        pytest.raises(TypeError, datatypes.latitude, None)
        pytest.raises(ValueError, datatypes.latitude, 'a')
        pytest.raises(ValueError, datatypes.latitude, 92.0)
        pytest.raises(ValueError, datatypes.latitude, -92.0)
        pytest.raises(TypeError, datatypes.latitude, 1, 2)

    def test_latitude_str(self):
        lat = datatypes.latitude(27.3375)
        assert "27.3375" == repr(lat)
        assert u"27°20'15.000000\"N" == six.text_type(lat)

        lat = datatypes.latitude(-27.3375)
        assert "-27.3375" == repr(lat)
        assert u"27°20'15.000000\"S" == six.text_type(lat)

    def test_longitude_valid(self):
        assert 30 == datatypes.longitude(30)
        assert -30 == datatypes.longitude(-30)
        assert 180.0 == datatypes.longitude(180.0)
        assert -180.0 == datatypes.longitude(-180.0)
        assert 42.0 == datatypes.longitude("42.0")
        assert -42.0 == datatypes.longitude("-42.0")
        assert 42.0 == datatypes.longitude(float(42.0))
        assert -42.0 == datatypes.longitude(float(-42.0))
        assert 42.0 == datatypes.longitude(datatypes.longitude(42.0))
        assert -42.0 == datatypes.longitude(datatypes.longitude(-42.0))

    def test_longitude_invalid(self):
        pytest.raises(TypeError, datatypes.longitude, None)
        pytest.raises(ValueError, datatypes.longitude, 'a')
        pytest.raises(ValueError, datatypes.longitude, 182.0)
        pytest.raises(ValueError, datatypes.longitude, -182.0)
        pytest.raises(TypeError, datatypes.longitude, 1, 2)

    def test_longitude_str(self):
        lat = datatypes.longitude(27.3375)
        assert "27.3375" == repr(lat)
        assert u"027°20'15.000000\"E" == six.text_type(lat)

        lat = datatypes.longitude(-27.3375)
        assert "-27.3375" == repr(lat)
        assert u"027°20'15.000000\"W" == six.text_type(lat)

    def test_latlng_valid(self):
        assert (10.0, 20.0) == datatypes.latlng(10, 20)
        assert (10.0, 20.0) == datatypes.latlng('10', '20')
        assert (10.0, 20.0) == datatypes.latlng(datatypes.latitude(10), datatypes.longitude(20))
        assert (10.0, 20.0) == datatypes.latlng((10, 20))
        assert (90.0, 180.0) == datatypes.latlng(90, 180)
        assert (-90.0, -180.0) == datatypes.latlng(-90, -180)

    def test_latlng_invalid(self):
        pytest.raises(TypeError, datatypes.latlng, None)
        pytest.raises(TypeError, datatypes.latlng, 1)
        pytest.raises(TypeError, datatypes.latlng, 1, 2, 3)
        pytest.raises(TypeError, datatypes.latlng, (1, 2, 3))
        pytest.raises(ValueError, datatypes.latlng, 90, 'a')
        pytest.raises(ValueError, datatypes.latlng, 100, 100)

    def test_latlng_str(self):
        ll = datatypes.latlng(27.3375, -27.3375)
        assert "latlng(27.3375, -27.3375)" == repr(ll)
        assert u"(27°20'15.000000\"N, 027°20'15.000000\"W)" == six.text_type(ll)

    def test_latlng_properties(self):
        ll = datatypes.latlng(27.3375, -27.3375)
        assert 27.3375 == ll.lat
        assert -27.3375 == ll.lng

    def test_point_valid(self):
        assert (1, 2) == datatypes.point(1, 2)
        assert (1, 2) == datatypes.point('1', '2')
        assert (1, 2) == datatypes.point((1, 2))
        assert (1, 2, 3) == datatypes.point(1, 2, 3)
        assert (1, 2, 3) == datatypes.point('1', '2', '3')
        assert (1, 2, 3) == datatypes.point((1, 2, 3))

    def test_point_invalid(self):
        pytest.raises(TypeError, datatypes.point, None)
        pytest.raises(TypeError, datatypes.point, 1)
        pytest.raises(TypeError, datatypes.point, 1, 2, 3, 4)
        pytest.raises(TypeError, datatypes.point, (1, 2, 3, 4))
        pytest.raises(ValueError, datatypes.point, 90, 'a', 1)

    def test_point_str(self):
        p = datatypes.point(1, 2)
        assert "point(1.000000, 2.000000)" == repr(p)
        assert "(1.000000, 2.000000)" == str(p)

        p = datatypes.point(1, 2, 3)
        assert "point(1.000000, 2.000000, 3.000000)" == repr(p)
        assert "(1.000000, 2.000000, 3.000000)" == str(p)

    def test_point_properties(self):
        p = datatypes.point(1, 2)
        assert 1 == p.x
        assert 2 == p.y
        pytest.raises(AttributeError, lambda: p.z)
        assert not p.is_3d

        p = datatypes.point(1, 2, 3)
        assert 1 == p.x
        assert 2 == p.y
        assert 3 == p.z
        assert p.is_3d
