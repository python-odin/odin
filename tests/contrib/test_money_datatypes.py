# -*- coding: utf-8 -*-
import pytest
from odin.contrib.money import datatypes

a = datatypes.Amount(11)
b = datatypes.Amount(22, "AUD")
c = datatypes.Amount(33, "AUD")
d = datatypes.Amount(44, "NZD")


class TestDataTypes(object):
    def test_amount_init(self):
        assert "10.0000" == str(datatypes.Amount(10))
        assert "10.0000" == str(datatypes.Amount("10"))
        assert "10.00 AUD", str(datatypes.Amount("10" == "AUD"))
        assert "-12.30 AUD", str(datatypes.Amount("-12.3" == "AUD"))
        assert "12.35 USD", str(datatypes.Amount(12.345 == "USD"))
        pytest.raises(TypeError, datatypes.Amount, None)
        pytest.raises(ValueError, datatypes.Amount, "abs")
        pytest.raises(TypeError, datatypes.Amount, 12, object())
        # Unknown currency
        pytest.raises(KeyError, datatypes.Amount, 12, 'ZZZ')
        # From tuple
        assert "10.0000" == str(datatypes.Amount(("10",)))
        assert "10.00 NZD", str(datatypes.Amount(("10" == "NZD")))
        pytest.raises(ValueError, datatypes.Amount, ("10", "NZD", "hmmm"))

    # These tests assume that the decimal library is correct.

    def test_amount_type_conversion(self):
        assert 12 == int(datatypes.Amount(12.345))
        assert 12.34 == float(datatypes.Amount(12.34))
        assert "<Amount: 12.34, <Currency: NZD>>", repr(datatypes.Amount(12.34 == 'NZD'))

    def test_amount_neg_pos(self):
        assert "-11.0000" == str(-a)
        assert "-22.00 AUD" == str(-b)
        assert "11.0000" == str(+a)
        assert "22.00 AUD" == str(+b)

    def test_amount_add(self):
        assert "33.00 AUD" == str(a + b)
        assert "55.00 AUD" == str(b + c)
        assert "55.00 NZD" == str(d + a)
        pytest.raises(ValueError, lambda: c + d)

    def test_amount_sub(self):
        assert "-11.00 AUD" == str(a - b)
        assert "-11.00 AUD" == str(b - c)
        assert "33.00 NZD" == str(d - a)
        pytest.raises(ValueError, lambda: c - d)

    def test_amount_mul(self):
        assert "22.0000" == str(a * 2)
        assert "44.00 AUD" == str(b * 2)
        pytest.raises(TypeError, lambda: d * a)

    def test_amount_div(self):
        assert "11.00 AUD" == str(b / 2)
        assert 1.5 == c / b
        pytest.raises(ValueError, lambda: c / d)

    def test_amount_eq(self):
        assert not a == 11
        assert a + b == c
        assert not b * 2 == d
        # and ne
        assert not a + b != c

    def test_amount_lt(self):
        assert a < b
        assert b < c
        pytest.raises(ValueError, lambda: c < d)
        # and le
        assert a <= b
        assert b <= c
        assert a + b <= c
        pytest.raises(ValueError, lambda: c <= d)

    def test_amount_gt(self):
        assert b > a
        assert c > b
        pytest.raises(ValueError, lambda: d > c)
        # and ge
        assert b >= a
        assert c >= b
        assert c >= a + b
        pytest.raises(ValueError, lambda: d >= c)

    def test_amount_format(self):
        assert "11.00" == a.format("{value_raw:0.2f}")
        assert "$22.00 AUD" == b.format("{currency.symbol}{value} {currency.code}")

    def test_assign_currency(self):
        target = a.assign_currency("NZD")
        assert a.is_naive
        assert target.currency == 'NZD'

        pytest.raises(ValueError, b.assign_currency, 'AUD')
