# -*- coding: utf-8 -*-
import unittest
from odin.contrib.money import datatypes

a = datatypes.Amount(11)
b = datatypes.Amount(22, "AUD")
c = datatypes.Amount(33, "AUD")
d = datatypes.Amount(44, "NZD")


class DataTypesTestCase(unittest.TestCase):
    def test_amount_init(self):
        self.assertEqual("10", str(datatypes.Amount(10)))
        self.assertEqual("10", str(datatypes.Amount("10")))
        self.assertEqual("10.00 AUD", str(datatypes.Amount("10", "AUD")))
        self.assertEqual("-12.30 AUD", str(datatypes.Amount("-12.3", "AUD")))
        self.assertEqual("12.35 USD", str(datatypes.Amount(12.345, "USD")))
        self.assertRaises(TypeError, datatypes.Amount, None)
        self.assertRaises(ValueError, datatypes.Amount, "abs")
        self.assertRaises(TypeError, datatypes.Amount, 12, object())
        # Unknown currency
        self.assertRaises(KeyError, datatypes.Amount, 12, 'ZZZ')
        # From tuple
        self.assertEqual("10", str(datatypes.Amount(("10",))))
        self.assertEqual("10.00 NZD", str(datatypes.Amount(("10", "NZD"))))
        self.assertRaises(ValueError, datatypes.Amount, ("10", "NZD", "hmmm"))

    # These tests assume that the decimal library is correct.

    def test_amount_type_conversion(self):
        self.assertEqual(12, int(datatypes.Amount(12.345)))
        self.assertEqual(12.34, float(datatypes.Amount(12.34)))
        self.assertEqual("<Amount: 12.34, <Currency: NZD>>", repr(datatypes.Amount(12.34, 'NZD')))

    def test_amount_neg_pos(self):
        self.assertEqual("-11", str(-a))
        self.assertEqual("-22.00 AUD", str(-b))
        self.assertEqual("11", str(+a))
        self.assertEqual("22.00 AUD", str(+b))

    def test_amount_add(self):
        self.assertEqual("33.00 AUD", str(a + b))
        self.assertEqual("55.00 AUD", str(b + c))
        self.assertEqual("55.00 NZD", str(d + a))
        self.assertRaises(ValueError, lambda: c + d)

    def test_amount_sub(self):
        self.assertEqual("-11.00 AUD", str(a - b))
        self.assertEqual("-11.00 AUD", str(b - c))
        self.assertEqual("33.00 NZD", str(d - a))
        self.assertRaises(ValueError, lambda: c - d)

    def test_amount_mul(self):
        self.assertEqual("22", str(a * 2))
        self.assertEqual("44.00 AUD", str(b * 2))
        self.assertRaises(TypeError, lambda: d * a)

    def test_amount_div(self):
        self.assertEqual("11.00 AUD", str(b / 2))
        self.assertEqual(1.5, c / b)
        self.assertRaises(ValueError, lambda: c / d)

    def test_amount_eq(self):
        self.assertFalse(a == 11)
        self.assertTrue(a + b == c)
        self.assertFalse(b * 2 == d)
        # and ne
        self.assertFalse(a + b != c)

    def test_amount_lt(self):
        self.assertTrue(a < b)
        self.assertTrue(b < c)
        self.assertRaises(ValueError, lambda: c < d)
        # and le
        self.assertTrue(a <= b)
        self.assertTrue(b <= c)
        self.assertTrue(a + b <= c)
        self.assertRaises(ValueError, lambda: c <= d)

    def test_amount_gt(self):
        self.assertTrue(b > a)
        self.assertTrue(c > b)
        self.assertRaises(ValueError, lambda: d > c)
        # and ge
        self.assertTrue(b >= a)
        self.assertTrue(c >= b)
        self.assertTrue(c >= a + b)
        self.assertRaises(ValueError, lambda: d >= c)

    def test_amount_format(self):
        self.assertEqual("11.00", a.format("{value_raw:0.2f}"))
        self.assertEqual("$22.00 AUD", b.format("{currency.symbol}{value} {currency.code}"))

    def test_assign_currency(self):
        target = a.assign_currency("NZD")
        self.assertTrue(a.is_naive)
        self.assertTrue(target.currency == 'NZD')

        self.assertRaises(ValueError, b.assign_currency, 'AUD')
