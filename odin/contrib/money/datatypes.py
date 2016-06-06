# -*- coding: utf-8 -*-
from __future__ import division
import decimal
import six

__all__ = ('Currency', 'set_default_currency', 'Amount')


class Currency(object):
    """
    A monetary currency.
    """
    def __new__(cls, code, number, name="", symbol=u"", precision=2):
        self = object.__new__(cls)
        self.code = code
        self.number = number
        self.name = name
        self.symbol = symbol
        self.precision = precision
        return self

    def __eq__(self, other):
        if isinstance(other, Currency):
            return self.code == other.code
        if isinstance(other, str):
            return self.code == other
        return False

    def __repr__(self):
        return "<Currency: %s>" % self.code

    def __str__(self):
        if self.name:
            return "%s - %s" % (self.name, self.code)
        else:
            return self.code


CURRENCY = {}
# XXX is the currency code for no currency in ISO 4217
CURRENCY['XXX'] = DEFAULT_CURRENCY = NO_CURRENCY = Currency('XXX', 999, 'No Currency', '', 4)


def set_default_currency(code='XXX'):
    """
    Set the default currency (the one applied if no currency is specified)
    :param code:
    :return:
    """
    global DEFAULT_CURRENCY
    DEFAULT_CURRENCY = CURRENCY[code]


class Amount(tuple):
    """
    A monetary amount and the associated currency.
    """
    def __new__(cls, value=None, currency=None):
        if isinstance(value, (tuple, list)):
            if len(value) == 1:
                value = value[0]
            elif len(value) == 2:
                value, currency = value
            else:
                raise ValueError("expected tuple with a length of 1 or 2 got: %s" % len(value))

        if not isinstance(value, decimal.Decimal):
            try:
                value = decimal.Decimal(value)
            except decimal.InvalidOperation:
                raise ValueError("value is not a valid numerical amount: %s" % value)

        if currency is None:
            currency = DEFAULT_CURRENCY
        elif isinstance(currency, six.string_types):
            currency = CURRENCY[currency.upper()]
        elif not isinstance(currency, Currency):
            raise TypeError("unable to convert value into a valid currency: %s" % currency)

        return tuple.__new__(cls, (value, currency))

    # Type conversions

    def __float__(self):
        return float(self.value)

    def __int__(self):
        return int(self.value)

    def __str__(self):
        if self.currency == NO_CURRENCY:
            return self.format("{value}")
        else:
            return self.format("{value} {currency.code}")

    def __repr__(self):
        return self.format("<Amount: {value}, {currency!r}>")

    # Math operations

    def __round__(self, n=None):
        """
        Round the value to the specified.
        """
        return self.value.__round__(n or self.currency.precision)

    def __pos__(self):
        return Amount(self.value, self.currency)

    def __neg__(self):
        return Amount(-self.value, self.currency)

    def __add__(self, other):
        other_value, currency = self._pre_calculate(other)
        return Amount(self.value + other_value, currency)

    def __sub__(self, other):
        other_value, currency = self._pre_calculate(other)
        return Amount(self.value - other_value, currency)

    def __mul__(self, other):
        if isinstance(other, Amount):
            raise TypeError("monetary amounts can not be multiplied.")
        else:
            return Amount(self.value * decimal.Decimal(other), self.currency)

    def __truediv__(self, other):
        other_value, currency = self._pre_calculate(other)
        # If the other instance is a currency we return just a value.
        if isinstance(other, Amount):
            return self.value / other_value
        else:
            return Amount(self.value / other_value, currency)

    __radd__ = __add__
    __rsub__ = __sub__
    __rmul__ = __mul__
    __div__ = __rtruediv__ = __truediv__

    # Comparison operators

    def __eq__(self, other):
        if isinstance(other, Amount):
            return self.value == other.value and self.currency == other.currency
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        other_value, _ = self._pre_calculate(other)
        return self.value < other_value

    def __gt__(self, other):
        other_value, _ = self._pre_calculate(other)
        return self.value > other_value

    def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return self > other or self == other

    def _pre_calculate(self, other):
        """
        Handle any pre-calculation checks
        """
        if isinstance(other, Amount):
            other_value = other.value
            other_currency = other.currency
        else:
            other_value = decimal.Decimal(other)
            other_currency = NO_CURRENCY

        if self.currency == NO_CURRENCY:
            currency = other_currency
        elif other_currency == NO_CURRENCY:
            currency = self.currency
        elif self.currency != other.currency:
            raise ValueError("Cannot perform calculation on amounts of different currencies.")
        else:
            currency = self.currency

        return other_value, currency

    @property
    def value(self):
        return self[0]

    @property
    def currency(self):
        return self[1]

    @property
    def is_naive(self):
        """
        Boolean indicating if this field is assigned `NO_CURRENCY`.
        """
        return self.currency == NO_CURRENCY

    def format(self, format_string):
        """
        Format an amount.

        Internally this uses the python builtin string format method. The following fields are available for formatting:

        - *value*; value of the amount formatted to the precision defined by the currency
        - *value_raw*; the raw value used internally (a Decimal)
        - *currency*; the currency
          - *currency.symbol*; the symbol defined by the currency
          - *currency.code*; the code defined by the currency
          - *currency.number*; the number defined by the currency (currencies are assigned a number along with a code)
          - *currency.name*; the name defined by the currency

        Usage::

            > Amount(10, 'USD').format("{symbol}{value} {code}")
            $10.00 USD

        :param format_string:
        :return: formatted string

        """
        assert isinstance(format_string, six.string_types)
        return format_string.format(
            value=('{0:0.%if}' % self.currency.precision).format(self.value),
            value_raw=self.value,
            currency=self.currency,
        )

    def assign_currency(self, currency):
        """
        Assign a currency if this amount currently has no currency assigned.

        As an ``Amount`` is immutable this will return a new ``Amount`` instance.

        :param currency: Currency to apply.
        :return:

        """
        if not self.is_naive:
            raise ValueError("This amount is already assigned a currency.")
        return Amount(self.value, CURRENCY[currency])


# Currencies based off the latest ISO 4217 list of currencies
# Updated: 2014-08-29
CURRENCY['AED'] = Currency('AED', 784, 'UAE Dirham', u'', 2)
CURRENCY['AFN'] = Currency('AFN', 971, 'Afghani', u'؋', 2)
CURRENCY['ALL'] = Currency('ALL', 8, 'Lek', u'', 2)
CURRENCY['AMD'] = Currency('AMD', 51, 'Armenian Dram', u'', 2)
CURRENCY['ANG'] = Currency('ANG', 532, 'Netherlands Antillean Guilder', u'ƒ', 2)
CURRENCY['AOA'] = Currency('AOA', 973, 'Kwanza', u'', 2)
CURRENCY['ARS'] = Currency('ARS', 32, 'Argentine Peso', u'$', 2)
CURRENCY['AUD'] = Currency('AUD', 36, 'Australian Dollar', u'$', 2)
CURRENCY['AWG'] = Currency('AWG', 533, 'Aruban Florin', u'ƒ', 2)
CURRENCY['AZN'] = Currency('AZN', 944, 'Azerbaijanian Manat', u'ман', 2)
CURRENCY['BAM'] = Currency('BAM', 977, 'Convertible Mark', u'KM', 2)
CURRENCY['BBD'] = Currency('BBD', 52, 'Barbados Dollar', u'$', 2)
CURRENCY['BDT'] = Currency('BDT', 50, 'Taka', u'', 2)
CURRENCY['BGN'] = Currency('BGN', 975, 'Bulgarian Lev', u'', 2)
CURRENCY['BHD'] = Currency('BHD', 48, 'Bahraini Dinar', u'', 3)
CURRENCY['BIF'] = Currency('BIF', 108, 'Burundi Franc', u'', 0)
CURRENCY['BMD'] = Currency('BMD', 60, 'Bermudian Dollar', u'', 2)
CURRENCY['BND'] = Currency('BND', 96, 'Brunei Dollar', u'$', 2)
CURRENCY['BOB'] = Currency('BOB', 68, 'Boliviano', u'', 2)
CURRENCY['BOV'] = Currency('BOV', 984, 'Mvdol', u'', 2)
CURRENCY['BRL'] = Currency('BRL', 986, 'Brazilian Real', u'', 2)
CURRENCY['BSD'] = Currency('BSD', 44, 'Bahamian Dollar', u'', 2)
CURRENCY['BTN'] = Currency('BTN', 64, 'Ngultrum', u'', 2)
CURRENCY['BWP'] = Currency('BWP', 72, 'Pula', u'P', 2)
CURRENCY['BYR'] = Currency('BYR', 974, 'Belarussian Ruble', u'p.', 0)
CURRENCY['BZD'] = Currency('BZD', 84, 'Belize Dollar', u'BZ$', 2)
CURRENCY['CAD'] = Currency('CAD', 124, 'Canadian Dollar', u'$', 2)
CURRENCY['CDF'] = Currency('CDF', 976, 'Congolese Franc', u'', 2)
CURRENCY['CHE'] = Currency('CHE', 947, 'WIR Euro', u'', 2)
CURRENCY['CHF'] = Currency('CHF', 756, 'Swiss Franc', u'CHF', 2)
CURRENCY['CHW'] = Currency('CHW', 948, 'WIR Franc', u'', 2)
CURRENCY['CLF'] = Currency('CLF', 990, 'Unidad de Fomento', u'', 4)
CURRENCY['CLP'] = Currency('CLP', 152, 'Chilean Peso', u'$', 0)
CURRENCY['CNY'] = Currency('CNY', 156, 'Yuan Renminbi', u'¥', 2)
CURRENCY['COP'] = Currency('COP', 170, 'Colombian Peso', u'$', 2)
CURRENCY['COU'] = Currency('COU', 970, 'Unidad de Valor Real', u'', 2)
CURRENCY['CRC'] = Currency('CRC', 188, 'Costa Rican Colon', u'₡', 2)
CURRENCY['CUC'] = Currency('CUC', 931, 'Peso Convertible', u'', 2)
CURRENCY['CUP'] = Currency('CUP', 192, 'Cuban Peso', u'₱', 2)
CURRENCY['CVE'] = Currency('CVE', 132, 'Cabo Verde Escudo', u'', 2)
CURRENCY['CZK'] = Currency('CZK', 203, 'Czech Koruna', u'Kč', 2)
CURRENCY['DJF'] = Currency('DJF', 262, 'Djibouti Franc', u'', 0)
CURRENCY['DKK'] = Currency('DKK', 208, 'Danish Krone', u'kr', 2)
CURRENCY['DOP'] = Currency('DOP', 214, 'Dominican Peso', u'RD$', 2)
CURRENCY['DZD'] = Currency('DZD', 12, 'Algerian Dinar', u'', 2)
CURRENCY['EGP'] = Currency('EGP', 818, 'Egyptian Pound', u'£', 2)
CURRENCY['ERN'] = Currency('ERN', 232, 'Nakfa', u'', 2)
CURRENCY['ETB'] = Currency('ETB', 230, 'Ethiopian Birr', u'', 2)
CURRENCY['EUR'] = Currency('EUR', 978, 'Euro', u'€', 2)
CURRENCY['FJD'] = Currency('FJD', 242, 'Fiji Dollar', u'$', 2)
CURRENCY['FKP'] = Currency('FKP', 238, 'Falkland Islands Pound', u'£', 2)
CURRENCY['GBP'] = Currency('GBP', 826, 'Pound Sterling', u'£', 2)
CURRENCY['GEL'] = Currency('GEL', 981, 'Lari', u'', 2)
CURRENCY['GHS'] = Currency('GHS', 936, 'Ghana Cedi', u'¢', 2)
CURRENCY['GIP'] = Currency('GIP', 292, 'Gibraltar Pound', u'£', 2)
CURRENCY['GMD'] = Currency('GMD', 270, 'Dalasi', u'', 2)
CURRENCY['GNF'] = Currency('GNF', 324, 'Guinea Franc', u'', 0)
CURRENCY['GTQ'] = Currency('GTQ', 320, 'Quetzal', u'Q', 2)
CURRENCY['GYD'] = Currency('GYD', 328, 'Guyana Dollar', u'$', 2)
CURRENCY['HKD'] = Currency('HKD', 344, 'Hong Kong Dollar', u'$', 2)
CURRENCY['HNL'] = Currency('HNL', 340, 'Lempira', u'L', 2)
CURRENCY['HRK'] = Currency('HRK', 191, 'Croatian Kuna', u'kn', 2)
CURRENCY['HTG'] = Currency('HTG', 332, 'Gourde', u'', 2)
CURRENCY['HUF'] = Currency('HUF', 348, 'Forint', u'Ft', 2)
CURRENCY['IDR'] = Currency('IDR', 360, 'Rupiah', u'Rp', 2)
CURRENCY['ILS'] = Currency('ILS', 376, 'New Israeli Sheqel', u'₪', 2)
CURRENCY['INR'] = Currency('INR', 356, 'Indian Rupee', u'₹', 2)
CURRENCY['IQD'] = Currency('IQD', 368, 'Iraqi Dinar', u'', 3)
CURRENCY['IRR'] = Currency('IRR', 364, 'Iranian Rial', u'﷼', 2)
CURRENCY['ISK'] = Currency('ISK', 352, 'Iceland Krona', u'kr', 0)
CURRENCY['JMD'] = Currency('JMD', 388, 'Jamaican Dollar', u'J$', 2)
CURRENCY['JOD'] = Currency('JOD', 400, 'Jordanian Dinar', u'', 3)
CURRENCY['JPY'] = Currency('JPY', 392, 'Yen', u'¥', 0)
CURRENCY['KES'] = Currency('KES', 404, 'Kenyan Shilling', u'', 2)
CURRENCY['KGS'] = Currency('KGS', 417, 'Som', u'лв', 2)
CURRENCY['KHR'] = Currency('KHR', 116, 'Riel', u'៛', 2)
CURRENCY['KMF'] = Currency('KMF', 174, 'Comoro Franc', u'', 0)
CURRENCY['KPW'] = Currency('KPW', 408, 'North Korean Won', u'₩', 2)
CURRENCY['KRW'] = Currency('KRW', 410, 'Won', u'₩', 0)
CURRENCY['KWD'] = Currency('KWD', 414, 'Kuwaiti Dinar', u'', 3)
CURRENCY['KYD'] = Currency('KYD', 136, 'Cayman Islands Dollar', u'$', 2)
CURRENCY['KZT'] = Currency('KZT', 398, 'Tenge', u'лв', 2)
CURRENCY['LAK'] = Currency('LAK', 418, 'Kip', u'₭', 2)
CURRENCY['LBP'] = Currency('LBP', 422, 'Lebanese Pound', u'£', 2)
CURRENCY['LKR'] = Currency('LKR', 144, 'Sri Lanka Rupee', u'₨', 2)
CURRENCY['LRD'] = Currency('LRD', 430, 'Liberian Dollar', u'$', 2)
CURRENCY['LSL'] = Currency('LSL', 426, 'Loti', u'', 2)
CURRENCY['LTL'] = Currency('LTL', 440, 'Lithuanian Litas', u'Lt', 2)
CURRENCY['LYD'] = Currency('LYD', 434, 'Libyan Dinar', u'', 3)
CURRENCY['MAD'] = Currency('MAD', 504, 'Moroccan Dirham', u'', 2)
CURRENCY['MDL'] = Currency('MDL', 498, 'Moldovan Leu', u'', 2)
CURRENCY['MGA'] = Currency('MGA', 969, 'Malagasy Ariary', u'', 2)
CURRENCY['MKD'] = Currency('MKD', 807, 'Denar', u'ден', 2)
CURRENCY['MMK'] = Currency('MMK', 104, 'Kyat', u'', 2)
CURRENCY['MNT'] = Currency('MNT', 496, 'Tugrik', u'₮', 2)
CURRENCY['MOP'] = Currency('MOP', 446, 'Pataca', u'', 2)
CURRENCY['MRO'] = Currency('MRO', 478, 'Ouguiya', u'', 2)
CURRENCY['MUR'] = Currency('MUR', 480, 'Mauritius Rupee', u'₨', 2)
CURRENCY['MVR'] = Currency('MVR', 462, 'Rufiyaa', u'', 2)
CURRENCY['MWK'] = Currency('MWK', 454, 'Kwacha', u'', 2)
CURRENCY['MXN'] = Currency('MXN', 484, 'Mexican Peso', u'$', 2)
CURRENCY['MXV'] = Currency('MXV', 979, 'Mexican Unidad de Inversion (UDI)', u'', 2)
CURRENCY['MYR'] = Currency('MYR', 458, 'Malaysian Ringgit', u'RM', 2)
CURRENCY['MZN'] = Currency('MZN', 943, 'Mozambique Metical', u'MT', 2)
CURRENCY['NAD'] = Currency('NAD', 516, 'Namibia Dollar', u'$', 2)
CURRENCY['NGN'] = Currency('NGN', 566, 'Naira', u'₦', 2)
CURRENCY['NIO'] = Currency('NIO', 558, 'Cordoba Oro', u'C$', 2)
CURRENCY['NOK'] = Currency('NOK', 578, 'Norwegian Krone', u'kr', 2)
CURRENCY['NPR'] = Currency('NPR', 524, 'Nepalese Rupee', u'₨', 2)
CURRENCY['NZD'] = Currency('NZD', 554, 'New Zealand Dollar', u'$', 2)
CURRENCY['OMR'] = Currency('OMR', 512, 'Rial Omani', u'﷼', 3)
CURRENCY['PAB'] = Currency('PAB', 590, 'Balboa', u'B/.', 2)
CURRENCY['PEN'] = Currency('PEN', 604, 'Nuevo Sol', u'S/.', 2)
CURRENCY['PGK'] = Currency('PGK', 598, 'Kina', u'', 2)
CURRENCY['PHP'] = Currency('PHP', 608, 'Philippine Peso', u'₱', 2)
CURRENCY['PKR'] = Currency('PKR', 586, 'Pakistan Rupee', u'₨', 2)
CURRENCY['PLN'] = Currency('PLN', 985, 'Zloty', u'zł', 2)
CURRENCY['PYG'] = Currency('PYG', 600, 'Guarani', u'Gs', 0)
CURRENCY['QAR'] = Currency('QAR', 634, 'Qatari Rial', u'﷼', 2)
CURRENCY['RON'] = Currency('RON', 946, 'New Romanian Leu', u'lei', 2)
CURRENCY['RSD'] = Currency('RSD', 941, 'Serbian Dinar', u'Дин.', 2)
CURRENCY['RUB'] = Currency('RUB', 643, 'Russian Ruble', u'руб', 2)
CURRENCY['RWF'] = Currency('RWF', 646, 'Rwanda Franc', u'', 0)
CURRENCY['SAR'] = Currency('SAR', 682, 'Saudi Riyal', u'', 2)
CURRENCY['SBD'] = Currency('SBD', 90, 'Solomon Islands Dollar', u'$', 2)
CURRENCY['SCR'] = Currency('SCR', 690, 'Seychelles Rupee', u'₨', 2)
CURRENCY['SDG'] = Currency('SDG', 938, 'Sudanese Pound', u'', 2)
CURRENCY['SEK'] = Currency('SEK', 752, 'Swedish Krona', u'kr', 2)
CURRENCY['SGD'] = Currency('SGD', 702, 'Singapore Dollar', u'$', 2)
CURRENCY['SHP'] = Currency('SHP', 654, 'Saint Helena Pound', u'£', 2)
CURRENCY['SLL'] = Currency('SLL', 694, 'Leone', u'', 2)
CURRENCY['SOS'] = Currency('SOS', 706, 'Somali Shilling', u'S', 2)
CURRENCY['SRD'] = Currency('SRD', 968, 'Surinam Dollar', u'$', 2)
CURRENCY['SSP'] = Currency('SSP', 728, 'South Sudanese Pound', u'', 2)
CURRENCY['STD'] = Currency('STD', 678, 'Dobra', u'', 2)
CURRENCY['SVC'] = Currency('SVC', 222, 'El Salvador Colon', u'$', 2)
CURRENCY['SYP'] = Currency('SYP', 760, 'Syrian Pound', u'£', 2)
CURRENCY['SZL'] = Currency('SZL', 748, 'Lilangeni', u'', 2)
CURRENCY['THB'] = Currency('THB', 764, 'Baht', u'฿', 2)
CURRENCY['TJS'] = Currency('TJS', 972, 'Somoni', u'', 2)
CURRENCY['TMT'] = Currency('TMT', 934, 'Turkmenistan New Manat', u'', 2)
CURRENCY['TND'] = Currency('TND', 788, 'Tunisian Dinar', u'', 3)
CURRENCY['TOP'] = Currency('TOP', 776, 'Pa’anga', u'', 2)
CURRENCY['TRY'] = Currency('TRY', 949, 'Turkish Lira', u'₤', 2)
CURRENCY['TTD'] = Currency('TTD', 780, 'Trinidad and Tobago Dollar', u'TT$', 2)
CURRENCY['TWD'] = Currency('TWD', 901, 'New Taiwan Dollar', u'NT$', 2)
CURRENCY['TZS'] = Currency('TZS', 834, 'Tanzanian Shilling', u'', 2)
CURRENCY['UAH'] = Currency('UAH', 980, 'Hryvnia', u'₴', 2)
CURRENCY['UGX'] = Currency('UGX', 800, 'Uganda Shilling', u'', 0)
CURRENCY['USD'] = Currency('USD', 840, 'US Dollar', u'$', 2)
CURRENCY['USN'] = Currency('USN', 997, 'US Dollar (Next day)', u'', 2)
CURRENCY['UYI'] = Currency('UYI', 940, 'Uruguay Peso en Unidades Indexadas (URUIURUI)', u'', 0)
CURRENCY['UYU'] = Currency('UYU', 858, 'Peso Uruguayo', u'$U', 2)
CURRENCY['UZS'] = Currency('UZS', 860, 'Uzbekistan Sum', u'лв', 2)
CURRENCY['VEF'] = Currency('VEF', 937, 'Bolivar', u'Bs', 2)
CURRENCY['VND'] = Currency('VND', 704, 'Dong', u'₫', 0)
CURRENCY['VUV'] = Currency('VUV', 548, 'Vatu', u'', 0)
CURRENCY['WST'] = Currency('WST', 882, 'Tala', u'', 2)
CURRENCY['XAF'] = Currency('XAF', 950, 'CFA Franc BEAC', u'', 0)
CURRENCY['XCD'] = Currency('XCD', 951, 'East Caribbean Dollar', u'$', 2)
CURRENCY['XOF'] = Currency('XOF', 952, 'CFA Franc BCEAO', u'', 0)
CURRENCY['XPF'] = Currency('XPF', 953, 'CFP Franc', u'', 0)
CURRENCY['XTS'] = Currency('XTS', 963, 'Test currency', u'', 0)
CURRENCY['YER'] = Currency('YER', 886, 'Yemeni Rial', u'﷼', 2)
CURRENCY['ZAR'] = Currency('ZAR', 710, 'Rand', u'S', 2)
CURRENCY['ZMW'] = Currency('ZMW', 967, 'Zambian Kwacha', u'', 2)
CURRENCY['ZWL'] = Currency('ZWL', 932, 'Zimbabwe Dollar', u'Z$', 2)

# Additional special case as BTC is not a "real" currency.
CURRENCY['BTC'] = Currency('BTC', 0, 'Bitcoin', u'฿', 4)
