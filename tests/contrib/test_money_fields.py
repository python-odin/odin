# -*- coding: utf-8 -*-
import unittest
from odin.contrib.money import AmountField
from odin.contrib.money import Amount
from odin.exceptions import ValidationError

a = Amount(11)
b = Amount(22, "AUD")
c = Amount(33, "AUD")
d = Amount(44, "NZD")


class AmountFieldsTestCase(unittest.TestCase):
    # AmountField #############################################################

    def test_money_field(self):
        f = AmountField()
        self.assertRaises(ValidationError, f.clean, None)
        self.assertRaises(ValidationError, f.clean, 'a')
        self.assertEqual(a, f.clean(11))
        self.assertEqual(b, f.clean((22, 'AUD')))

    def test_money_field_1(self):
        f = AmountField(allowed_currencies=('NZD', 'AUD'))
        self.assertEqual(d, f.clean((44, 'NZD')))
        self.assertRaises(ValidationError, f.clean, (22, 'USD'))
