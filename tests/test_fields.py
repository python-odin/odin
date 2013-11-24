# -*- coding: utf-8 -*-
import unittest
import datetime
from odin import StringField, BooleanField, IntegerField, FloatField, DateTimeField
from odin.datetimeutil import UTC, utc
from odin.validators import MinLengthValidator, MinValueValidator, MaxValueValidator, MaxLengthValidator
from odin.exceptions import ValidationError


class FieldsTests(unittest.TestCase):
    def assertValidatorIn(self, validatorClass, validators):
        """
        Assert that the specified validator is in the validation list.
        :param validatorClass:
        :param validators:
        """
        for v in validators:
            if isinstance(v, validatorClass):
                return
        raise AssertionError("Validator %r was not found in list of validators." % validatorClass)

    def assertValidatorNotIn(self, validatorClass, validators):
        """
        Assert that the specified validator is not in the validation list.
        :param validatorClass:
        :param validators:
        """
        for v in validators:
            if isinstance(v, validatorClass):
                raise AssertionError("Validator %r was found in list of validators." % validatorClass)


    # BooleanField ############################################################

    def test_booleanfield_1(self):
        f = BooleanField()
        self.assertRaises(ValidationError, f.clean, None)
        self.assertRaises(ValidationError, f.clean, '')
        self.assertEqual(True, f.clean(True))
        self.assertEqual(True, f.clean(1))
        self.assertEqual(True, f.clean('Yes'))
        self.assertEqual(True, f.clean('true'))
        self.assertEqual(True, f.clean('T'))
        self.assertEqual(True, f.clean('1'))
        self.assertRaises(ValidationError, f.clean, 'Awesome!')
        self.assertEqual(False, f.clean(False))
        self.assertEqual(False, f.clean(0))
        self.assertEqual(False, f.clean('No'))
        self.assertEqual(False, f.clean('false'))
        self.assertEqual(False, f.clean('F'))
        self.assertEqual(False, f.clean('0'))


    # StringField #############################################################

    def test_stringfield_1(self):
        f = StringField()
        self.assertEqual('1', f.clean('1'))
        self.assertEqual('eek', f.clean('eek'))
        self.assertRaises(ValidationError, f.clean, None)
        self.assertEqual('[1, 2, 3]', f.clean([1, 2, 3]))
        self.assertEqual(f.max_length, None)
        self.assertValidatorNotIn(MaxLengthValidator, f.validators)

    def test_stringfield_2(self):
        f = StringField(null=True)
        self.assertEqual('1', f.clean('1'))
        self.assertEqual('eek', f.clean('eek'))
        self.assertEqual(None, f.clean(None))
        self.assertEqual('[1, 2, 3]', f.clean([1, 2, 3]))
        self.assertEqual(f.max_length, None)
        self.assertValidatorNotIn(MaxLengthValidator, f.validators)

    def test_stringfield_3(self):
        f = StringField(null=True, max_length=10)
        self.assertEqual(None, f.clean(None))
        self.assertEqual('', f.clean(''))
        self.assertEqual('12345', f.clean('12345'))
        self.assertEqual('1234567890', f.clean('1234567890'))
        self.assertRaises(ValidationError, f.clean, '1234567890a')
        self.assertEqual(f.max_length, 10)
        self.assertValidatorIn(MaxLengthValidator, f.validators)


    # IntegerField ############################################################

    def test_integerfield_1(self):
        f = IntegerField()
        self.assertRaises(ValidationError, f.clean, None)
        self.assertRaises(ValidationError, f.clean, 'abc')
        self.assertEqual(123, f.clean(123))
        self.assertEqual(123, f.clean('123'))
        self.assertEqual(123, f.clean(123.5))
        self.assertEqual(None, f.min_value)
        self.assertValidatorNotIn(MinValueValidator, f.validators)
        self.assertEqual(None, f.max_value)
        self.assertValidatorNotIn(MaxValueValidator, f.validators)

    def test_integerfield_2(self):
        f = IntegerField(null=True)
        self.assertEqual(None, f.clean(None))
        self.assertRaises(ValidationError, f.clean, 'abc')
        self.assertEqual(69, f.clean(69))
        self.assertEqual(69, f.clean('69'))
        self.assertEqual(69, f.clean(69.5))
        self.assertEqual(None, f.min_value)
        self.assertValidatorNotIn(MinValueValidator, f.validators)
        self.assertEqual(None, f.max_value)
        self.assertValidatorNotIn(MaxValueValidator, f.validators)

    def test_integerfield_3(self):
        f = IntegerField(min_value=50, max_value=100)
        self.assertRaises(ValidationError, f.clean, None)
        self.assertRaises(ValidationError, f.clean, 'abc')
        self.assertEqual(69, f.clean(69))
        self.assertEqual(69, f.clean('69'))
        self.assertEqual(69, f.clean(69.5))
        self.assertEqual(50, f.clean(50))
        self.assertEqual(100, f.clean(100))
        self.assertRaises(ValidationError, f.clean, 30)
        self.assertRaises(ValidationError, f.clean, 110)
        self.assertEqual(50, f.min_value)
        self.assertValidatorIn(MinValueValidator, f.validators)
        self.assertEqual(100, f.max_value)
        self.assertValidatorIn(MaxValueValidator, f.validators)

    # FloatField ##############################################################

    def test_floatfield_1(self):
        f = FloatField()
        self.assertRaises(ValidationError, f.clean, None)
        self.assertRaises(ValidationError, f.clean, 'abc')
        self.assertEqual(123, f.clean(123))
        self.assertEqual(123.5, f.clean('123.5'))
        self.assertEqual(123.5, f.clean(123.5))
        self.assertEqual(None, f.min_value)
        self.assertValidatorNotIn(MinValueValidator, f.validators)
        self.assertEqual(None, f.max_value)
        self.assertValidatorNotIn(MaxValueValidator, f.validators)

    def test_floatfield_2(self):
        f = FloatField(null=True)
        self.assertEqual(None, f.clean(None))
        self.assertRaises(ValidationError, f.clean, 'abc')
        self.assertEqual(69, f.clean(69))
        self.assertEqual(69.5, f.clean('69.5'))
        self.assertEqual(69.5, f.clean(69.5))
        self.assertEqual(None, f.min_value)
        self.assertValidatorNotIn(MinValueValidator, f.validators)
        self.assertEqual(None, f.max_value)
        self.assertValidatorNotIn(MaxValueValidator, f.validators)

    def test_floatfield_3(self):
        f = FloatField(min_value=50.5, max_value=100.4)
        self.assertRaises(ValidationError, f.clean, None)
        self.assertRaises(ValidationError, f.clean, 'abc')
        self.assertEqual(69, f.clean(69))
        self.assertEqual(69.5, f.clean('69.5'))
        self.assertEqual(69.5, f.clean(69.5))
        self.assertEqual(50.5, f.clean(50.5))
        self.assertEqual(100.4, f.clean(100.4))
        self.assertRaises(ValidationError, f.clean, 30)
        self.assertRaises(ValidationError, f.clean, 110)
        self.assertEqual(50.5, f.min_value)
        self.assertValidatorIn(MinValueValidator, f.validators)
        self.assertEqual(100.4, f.max_value)
        self.assertValidatorIn(MaxValueValidator, f.validators)

    # DateTimeField ###########################################################

    def test_datetimefield_1(self):
        f = DateTimeField(assume_local=False)
        self.assertRaises(ValidationError, f.clean, None)
        self.assertRaises(ValidationError, f.clean, 'abc')
        self.assertRaises(ValidationError, f.clean, 123)
        self.assertEqual(datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc), f.clean('2013-11-24T18:43:00.000Z'))
        self.assertEqual(datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc),
                         f.clean(datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc)))

    def test_datetimefield_2(self):
        f = DateTimeField(assume_local=False, null=True)
        self.assertEqual(None, f.clean(None))
        self.assertRaises(ValidationError, f.clean, 'abc')
        self.assertRaises(ValidationError, f.clean, 123)
        self.assertEqual(datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc), f.clean('2013-11-24T18:43:00.000Z'))
        self.assertEqual(datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc),
                         f.clean(datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc)))

    def test_datetimefield_tostring(self):
        f = DateTimeField(assume_local=False)
        self.assertEqual('2013-11-24T18:43:00.000Z', f.to_string(datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc)))
        self.assertEqual(None, f.to_string(None))
