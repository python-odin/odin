# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
from odin import exceptions
from odin.fields import Field, ScalarField
from odin.validators import EMPTY_VALUES
from .datatypes import latitude, longitude, latlng, point

__all__ = ('LatitudeField', 'LongitudeField', 'LatLngField', 'PointField')


class LatitudeField(ScalarField):
    """
    Field that contains a latitude value.
    """
    default_error_messages = {
        'invalid': "'%s' value must be a latitude.",
    }
    data_type_name = "Latitude"

    def to_python(self, value):
        if value in EMPTY_VALUES:
            return
        try:
            return latitude(value)
        except (ValueError, TypeError):
            msg = self.error_messages['invalid'] % value
            raise exceptions.ValidationError(msg)


class LongitudeField(ScalarField):
    """
    Field that contains a longitude value.
    """
    default_error_messages = {
        'invalid': "'%s' value must be a longitude.",
    }
    data_type_name = "Longitude"

    def to_python(self, value):
        if value in EMPTY_VALUES:
            return
        try:
            return longitude(value)
        except (ValueError, TypeError):
            msg = self.error_messages['invalid'] % value
            raise exceptions.ValidationError(msg)


class LatLngField(Field):
    """
    Field that contains a lat/long pair.
    """
    default_error_messages = {
        'invalid': "'%s' value must be a (latitude, longitude).",
    }
    data_type_name = "LatLng"

    def to_python(self, value):
        if value in EMPTY_VALUES:
            return
        try:
            return latlng(value)
        except (ValueError, TypeError):
            msg = self.error_messages['invalid'] % value
            raise exceptions.ValidationError(msg)


class PointField(Field):
    """
    Field that contains a point in cartesian space. This can be either 2D (on a plain) or 3D (includes a z-axis).
    """
    default_error_messages = {
        'invalid': "'%s' value must be a point in 2D or 3D cartesian space.",
    }
    data_type_name = "Point"

    def to_python(self, value):
        if value in EMPTY_VALUES:
            return
        try:
            return point(value)
        except (ValueError, TypeError):
            msg = self.error_messages['invalid'] % value
            raise exceptions.ValidationError(msg)
