# -*- coding: utf-8 -*-
import odin
from odin.contrib.money import AmountField
from odin.contrib.money import Amount
from odin.codecs import json_codec


class AmountResource(odin.Resource):
    class Meta:
        namespace = "odin.tests"

    a = AmountField(null=True)
    b = AmountField()
    c = AmountField()


class TestMoneySerialisation(object):
    def test_serialise(self):
        resource = AmountResource(
            a=None,
            b=Amount(10),
            c=Amount(22.02, 'AUD')
        )

        actual = json_codec.dumps(resource, sort_keys=True)

        assert (
            actual ==
            '{"$": "odin.tests.AmountResource", "a": null, "b": [10.0, "XXX"], "c": [22.02, "AUD"]}'
        )

    def test_deserialise(self):
        resource = json_codec.loads(
            '{"$": "odin.tests.AmountResource", "a": null, "b": 10, "c": [23.66, "AUD"]}'
        )

        assert None == resource.a
        assert Amount(10) == resource.b
        assert Amount(23.66, "AUD") == resource.c
