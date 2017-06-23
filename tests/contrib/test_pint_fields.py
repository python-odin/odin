# -*- coding: utf-8 -*-
import pytest

from odin.exceptions import ValidationError

try:
    from odin.contrib.pint.fields import PintField, FloatField
    from odin.contrib.pint.units import registry
except ImportError:
    pass  # Pint is not available to pypy
else:

    class TestPintFields(object):
        # PintField ###############################################################

        def test_pintfield_init(self):
            pytest.raises(ValueError, PintField, None)

        # FloatField ##############################################################

        def test_floatfield_1(self):
            f = FloatField('kWh')
            pytest.raises(ValidationError, f.clean, None)
            pytest.raises(ValidationError, f.clean, 10.2 * registry.meter)
            pytest.raises(ValidationError, f.clean, 'abc')
            assert 10.2 * registry.kilowatt_hour == f.clean(10.2 * registry.kilowatt_hour)
            assert 10.2 * registry['kWh'] == f.clean(10.2)
            assert 10.2 * registry['kWh'] == f.clean((10.2, 'kWh'))
            assert 10.2 * registry['kWh'] == f.clean((10.2, registry.kilowatt_hour))
            assert 10.2 * registry.watt_hour == f.clean(10.2 * registry.watt_hour)
