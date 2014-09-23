# -*- coding: utf-8 -*-
import unittest
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


class MoneySerialisationTestCase(unittest.TestCase):
    def test_serialise(self):
        resource = AmountResource(
            a=None,
            b=Amount(10),
            c=Amount(22.02, 'AUD')
        )

        actual = json_codec.dumps(resource, sort_keys=True)

        self.assertEqual(
            actual,
            '{"$": "odin.tests.AmountResource", "a": null, "b": [10.0, "XXX"], "c": [22.02, "AUD"]}'
        )

    def test_deserialise(self):
        resource = json_codec.loads(
            '{"$": "odin.tests.AmountResource", "a": null, "b": 10, "c": [23.66, "AUD"]}'
        )

        self.assertEqual(None, resource.a)
        self.assertEqual(Amount(10), resource.b)
        self.assertEqual(Amount(23.66, "AUD"), resource.c)
