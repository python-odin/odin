# -*- coding: utf-8 -*-
import odin
from odin.contrib.geo import (
    LatitudeField, LongitudeField, LatLngField, PointField,
    latitude, longitude, latlng, point
)
from odin.codecs import json_codec


class GeoResource(odin.Resource):
    class Meta:
        namespace = "odin.tests"

    lat_a = LatitudeField(null=True)
    lat_b = LatitudeField()
    lat_c = LatitudeField()
    lng_a = LongitudeField(null=True)
    lng_b = LongitudeField()
    lng_c = LongitudeField()
    latlng_a = LatLngField(null=True)
    latlng_b = LatLngField()
    point_a = PointField(null=True)
    point_b = PointField()


class TestGeoSerialisation(object):
    def test_serialise(self):
        resource = GeoResource(
            lat_a=None,
            lat_b=latitude(23.67),
            lat_c=latitude(-23.67),
            lng_a=None,
            lng_b=longitude(123.56),
            lng_c=longitude(-123.56),
            latlng_a=None,
            latlng_b=latlng(23.67, -123.56),
            point_a=None,
            point_b=point(66.66, -33.33)
        )

        actual = json_codec.dumps(resource, sort_keys=True)

        assert (
            actual ==
            '{"$": "odin.tests.GeoResource", '
            '"lat_a": null, "lat_b": 23.67, "lat_c": -23.67, '
            '"latlng_a": null, "latlng_b": [23.67, -123.56], '
            '"lng_a": null, "lng_b": 123.56, "lng_c": -123.56, '
            '"point_a": null, "point_b": [66.66, -33.33]}'
        )

    def test_deserialise(self):
        resource = json_codec.loads(
            '{"$": "odin.tests.GeoResource", '
            '"lat_a": null, "lat_b": 23.67, "lat_c": -23.67, '
            '"latlng_a": null, "latlng_b": [23.67, -123.56], '
            '"lng_a": null, "lng_b": 123.56, "lng_c": -123.56, '
            '"point_a": null, "point_b": [66.66, -33.33]}'
        )

        assert None == resource.lat_a
        assert latitude(23.67) == resource.lat_b
        assert latitude(-23.67) == resource.lat_c
        assert None == resource.lng_a
        assert longitude(123.56) == resource.lng_b
        assert longitude(-123.56) == resource.lng_c
        assert None == resource.latlng_a
        assert latlng(23.67, -123.56) == resource.latlng_b
        assert None == resource.point_a
        assert point(66.66, -33.33) == resource.point_b
