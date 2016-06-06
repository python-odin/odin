# -*- coding: utf-8 -*-
import pytest
from odin.contrib.geo.datatypes import latitude, longitude, latlng, point
from odin.contrib.geo.fields import LatitudeField, LongitudeField, LatLngField, PointField
from odin.exceptions import ValidationError


class TestGeoFields(object):
    # LatitudeField ###########################################################

    def test_latitude_field(self):
        f = LatitudeField()
        pytest.raises(ValidationError, f.clean, None)
        pytest.raises(ValidationError, f.clean, 'a')
        pytest.raises(ValidationError, f.clean, 92)
        pytest.raises(ValidationError, f.clean, -92)
        assert 12.345 == f.clean(12.345)
        assert -12.345 == f.clean(-12.345)
        assert 12.345 == f.clean('12.345')
        assert isinstance(f.clean(12.345), latitude)

    # LongitudeField ##########################################################

    def test_longitude_field(self):
        f = LongitudeField()
        pytest.raises(ValidationError, f.clean, None)
        pytest.raises(ValidationError, f.clean, 'a')
        pytest.raises(ValidationError, f.clean, 182)
        pytest.raises(ValidationError, f.clean, -182)
        assert 123.456 == f.clean(123.456)
        assert -123.456 == f.clean(-123.456)
        assert 123.456 == f.clean('123.456')
        assert isinstance(f.clean(122.456), longitude)

    # LatLngField #############################################################

    def test_latlng_field(self):
        f = LatLngField()
        pytest.raises(ValidationError, f.clean, None)
        pytest.raises(ValidationError, f.clean, 'a')
        pytest.raises(ValidationError, f.clean, [])
        pytest.raises(ValidationError, f.clean, [12.345])
        pytest.raises(ValidationError, f.clean, [92, 123.345])
        pytest.raises(ValidationError, f.clean, [12.345, 182])

        assert (12.345, 123.456) == f.clean((12.345, 123.456))
        assert (12.345, 123.456) == f.clean(('12.345', '123.456'))
        assert isinstance(f.clean((12.345, 123.456)), latlng)

    # PointField ##############################################################

    def test_point_field(self):
        f = PointField()
        pytest.raises(ValidationError, f.clean, None)
        pytest.raises(ValidationError, f.clean, 'a')
        pytest.raises(ValidationError, f.clean, [])
        pytest.raises(ValidationError, f.clean, [1])
        pytest.raises(ValidationError, f.clean, [1, 2, 3, 4])
        pytest.raises(ValidationError, f.clean, [1, 2, 'a', 4])

        assert (1, 2) == f.clean((1, 2))
        assert (1, 2) == f.clean(('1', '2'))
        assert (1, 2, 3) == f.clean((1, 2, 3))
        assert (1, 2, 3) == f.clean(('1', '2', '3'))
        assert isinstance(f.clean((1, 2)), point)
        assert isinstance(f.clean((1, 2, 3)), point)
