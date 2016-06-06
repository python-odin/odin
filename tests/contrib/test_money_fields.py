# -*- coding: utf-8 -*-
import pytest
from odin.contrib.money import AmountField
from odin.contrib.money import Amount
from odin.exceptions import ValidationError

a = Amount(11)
b = Amount(22, "AUD")
c = Amount(33, "AUD")
d = Amount(44, "NZD")


class TestAmountFields(object):
    # AmountField #############################################################

    def test_money_field(self):
        f = AmountField()
        pytest.raises(ValidationError, f.clean, None)
        pytest.raises(ValidationError, f.clean, 'a')
        assert a == f.clean(11)
        assert b == f.clean((22, 'AUD'))

    def test_money_field_1(self):
        f = AmountField(allowed_currencies=('NZD', 'AUD'))
        assert d == f.clean((44, 'NZD'))
        pytest.raises(ValidationError, f.clean, (22, 'USD'))
