# -*- coding: utf-8 -*-
from copy import deepcopy
import unittest
import datetime
from odin.fields import *
from odin.fields import Field
from odin.datetimeutil import utc
from odin.fields.virtual import VirtualField
from odin.validators import MinValueValidator, MaxValueValidator, MaxLengthValidator, RegexValidator
from odin.exceptions import ValidationError


class ObjectValue(object):
    pass


class TestValidator(object):
    message = 'Default message'
    code = 'test_code'

    def __init__(self, fail, *params):
        self.fail = fail
        self.params = params

    def __call__(self, value):
        if self.fail:
            raise ValidationError(code=self.code, message=self.message, params=self.params)


class FieldTestCase(unittest.TestCase):
    def test_error_messages_no_overrides(self):
        target = Field()

        self.assertDictEqual({
            'invalid_choice': 'Value %r is not a valid choice.',
            'null': 'This field cannot be null.',
            'required': 'This field is required.',
        }, target.error_messages)

    def test_error_messages_override_add(self):
        target = Field(error_messages={
            'null': 'Override',
            'other': 'Other Value',
        })

        self.assertDictEqual({
            'invalid_choice': 'Value %r is not a valid choice.',
            'null': 'Override',
            'required': 'This field is required.',
            'other': 'Other Value',
        }, target.error_messages)

    def test_set_attributes_from_name(self):
        target = Field()
        target.set_attributes_from_name("test_name")

        self.assertEqual("test_name", target.name)
        self.assertEqual("test_name", target.attname)
        self.assertEqual("test name", target.verbose_name)
        self.assertEqual("test names", target.verbose_name_plural)

    def test_set_attributes_from_name_with_name(self):
        target = Field(name="init_name")
        target.set_attributes_from_name("test_name")

        self.assertEqual("init_name", target.name)
        self.assertEqual("test_name", target.attname)
        self.assertEqual("init name", target.verbose_name)
        self.assertEqual("init names", target.verbose_name_plural)

    def test_set_attributes_from_name_with_verbose_name(self):
        target = Field(verbose_name="init Verbose Name")
        target.set_attributes_from_name("test_name")

        self.assertEqual("test_name", target.name)
        self.assertEqual("test_name", target.attname)
        self.assertEqual("init Verbose Name", target.verbose_name)
        self.assertEqual("init Verbose Names", target.verbose_name_plural)

    def test_has_default(self):
        target = Field()

        self.assertFalse(target.has_default())

    def test_has_default_supplied(self):
        target = Field(default="123")

        self.assertTrue(target.has_default())

    def test_get_default(self):
        target = Field()

        self.assertIsNone(target.get_default())

    def test_get_default_supplied(self):
        target = Field(default="123")

        self.assertEqual("123", target.get_default())

    def test_get_default_callable(self):
        target = Field(default=lambda: "321")

        self.assertEqual("321", target.get_default())

    def test_value_from_object(self):
        target = Field()
        target.set_attributes_from_name("test_name")

        an_obj = ObjectValue()
        setattr(an_obj, "test_name", "test_value")

        actual = target.value_from_object(an_obj)
        self.assertEqual("test_value", actual)

    def test__repr(self):
        target = Field()
        self.assertEqual("<odin.fields.Field>", repr(target))
        target.set_attributes_from_name("eek")
        self.assertEqual("<odin.fields.Field: eek>", repr(target))

    def test__deep_copy(self):
        field = Field(name="Test")
        target_copy = deepcopy(field)
        target_assign = field
        self.assertIs(field, target_assign)
        self.assertIsNot(field, target_copy)
        self.assertEqual(field.name, target_copy.name)

    def test_run_validators_and_override_validator_message(self):
        target = Field(error_messages={'test_code': 'Override message'}, validators=[TestValidator(True)])

        try:
            target.run_validators("Placeholder")
        except ValidationError as ve:
            self.assertEqual('Override message', ve.messages[0])
        else:
            raise AssertionError("Validation Error not raised.")

    def test_run_validators_and_override_validator_message_with_params(self):
        target = Field(error_messages={'test_code': 'Override message: %s'}, validators=[TestValidator(True, "123")])

        try:
            target.run_validators("Placeholder")
        except ValidationError as ve:
            self.assertEqual(['Override message: 123'], ve.messages)
        else:
            raise AssertionError("Validation Error not raised.")

    def test_default_to_python_raises_not_implemented(self):
        target = Field()
        self.assertRaises(NotImplementedError, target.to_python, "Anything...")


class TestVirtualField(VirtualField):
    pass


class VirtualFieldTestCase(unittest.TestCase):
    def test_creation_counter(self):
        current_count = VirtualField.creation_counter
        next_count = current_count + 1
        target = VirtualField()

        assert VirtualField.creation_counter == next_count
        assert target.creation_counter == current_count
        assert hash(target) == current_count

    def test_repr(self):
        target = TestVirtualField()
        self.assertEqual("<tests.test_fields.TestVirtualField>", repr(target))
        target.set_attributes_from_name("eek")
        self.assertEqual("<tests.test_fields.TestVirtualField: eek>", repr(target))

    def test_default_descriptor_behaviour(self):
        class TestObj(object):
            test_field = VirtualField()
        target = TestObj()

        with self.assertRaises(NotImplementedError):
            _ = target.test_field

        with self.assertRaises(AttributeError) as cm:
            target.test_field = 123

        self.assertEqual("Read only", str(cm.exception))


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

    # URLField ################################################################

    def test_urlfield_1(self):
        f = UrlField()
        self.assertEqual('http://www.github.com', f.clean('http://www.github.com'))
        self.assertRaises(ValidationError, f.clean, 'eek')
        self.assertRaises(ValidationError, f.clean, None)
        self.assertEqual(f.max_length, None)
        self.assertValidatorIn(RegexValidator, f.validators)

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

    # DateField ###############################################################

    def test_datefield_1(self):
        f = DateField()
        self.assertRaises(ValidationError, f.clean, None)
        self.assertRaises(ValidationError, f.clean, 'abc')
        self.assertRaises(ValidationError, f.clean, 123)
        self.assertEqual(datetime.date(2013, 11, 24), f.clean('2013-11-24'))
        self.assertEqual(datetime.date(2013, 11, 24), f.clean(datetime.date(2013, 11, 24)))
        self.assertEqual(datetime.date(2013, 11, 24), f.clean(datetime.datetime(2013, 11, 24, 1, 14)))

    def test_datefield_2(self):
        f = DateField(null=True)
        self.assertEqual(None, f.clean(None))
        self.assertRaises(ValidationError, f.clean, 'abc')
        self.assertRaises(ValidationError, f.clean, 123)
        self.assertEqual(datetime.date(2013, 11, 24), f.clean('2013-11-24'))
        self.assertEqual(datetime.date(2013, 11, 24), f.clean(datetime.date(2013, 11, 24)))
        self.assertEqual(datetime.date(2013, 11, 24), f.clean(datetime.datetime(2013, 11, 24, 1, 14)))

    # TimeField ###############################################################

    def test_timefield_1(self):
        f = TimeField(assume_local=False)
        self.assertRaises(ValidationError, f.clean, None)
        self.assertRaises(ValidationError, f.clean, 'abc')
        self.assertRaises(ValidationError, f.clean, 123)
        self.assertEqual(datetime.time(18, 43, tzinfo=utc), f.clean('18:43:00.000Z'))
        self.assertEqual(datetime.time(18, 43, tzinfo=utc), f.clean(datetime.time(18, 43, tzinfo=utc)))

    def test_timefield_2(self):
        f = TimeField(assume_local=False, null=True)
        self.assertEqual(None, f.clean(None))
        self.assertRaises(ValidationError, f.clean, 'abc')
        self.assertRaises(ValidationError, f.clean, 123)
        self.assertEqual(datetime.time(18, 43, tzinfo=utc), f.clean('18:43:00.000Z'))
        self.assertEqual(datetime.time(18, 43, tzinfo=utc), f.clean(datetime.time(18, 43, tzinfo=utc)))

    # DateTimeField ###########################################################

    def test_datetimefield_1(self):
        f = DateTimeField(assume_local=False)
        self.assertRaises(ValidationError, f.clean, None)
        self.assertRaises(ValidationError, f.clean, 'abc')
        self.assertRaises(ValidationError, f.clean, 123)
        self.assertEqual(datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc), f.clean('2013-11-24T18:43:00.000Z'))
        self.assertEqual(datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc), f.clean('2013-11-24 18:43:00.000Z'))
        self.assertEqual(datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc),
                         f.clean(datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc)))

    def test_datetimefield_2(self):
        f = DateTimeField(assume_local=False, null=True)
        self.assertEqual(None, f.clean(None))
        self.assertRaises(ValidationError, f.clean, 'abc')
        self.assertRaises(ValidationError, f.clean, 123)
        self.assertEqual(datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc), f.clean('2013-11-24T18:43:00.000Z'))
        self.assertEqual(datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc), f.clean('2013-11-24 18:43:00.000Z'))
        self.assertEqual(datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc),
                         f.clean(datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc)))

    # HttpDateTimeField #######################################################

    def test_httpdatetimefield_1(self):
        f = HttpDateTimeField()
        self.assertRaises(ValidationError, f.clean, None)
        self.assertRaises(ValidationError, f.clean, 'abc')
        self.assertRaises(ValidationError, f.clean, 123)
        self.assertEqual(datetime.datetime(2012, 8, 29, 17, 12, 58, tzinfo=utc),
                         f.clean('Wed Aug 29 17:12:58 +0000 2012'))
        self.assertEqual(datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc),
                         f.clean(datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc)))

    def test_httpdatetimefield_2(self):
        f = HttpDateTimeField(null=True)
        self.assertEqual(None, f.clean(None))
        self.assertRaises(ValidationError, f.clean, 'abc')
        self.assertRaises(ValidationError, f.clean, 123)
        self.assertEqual(datetime.datetime(2012, 8, 29, 17, 12, 58, tzinfo=utc),
                         f.clean('Wed Aug 29 17:12:58 +0000 2012'))
        self.assertEqual(datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc),
                         f.clean(datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc)))

    # DictField ###############################################################

    def test_dictfield_1(self):
        f = DictField()
        self.assertRaises(ValidationError, f.clean, None)
        self.assertRaises(ValidationError, f.clean, 'abc')
        self.assertRaises(ValidationError, f.clean, 123)
        self.assertEqual({}, f.clean({}))
        self.assertEqual({'foo': 'bar'}, f.clean({'foo': 'bar'}))
        self.assertEqual(f.default, dict)

    def test_dictfield_2(self):
        f = DictField(null=True)
        self.assertEqual(None, f.clean(None))
        self.assertEqual({}, f.clean({}))
        self.assertRaises(ValidationError, f.clean, 'abc')
        self.assertRaises(ValidationError, f.clean, 123)
        self.assertEqual({'foo': 'bar'}, f.clean({'foo': 'bar'}))

    # ArrayField ##############################################################

    def test_arrayfield_1(self):
        f = ArrayField()
        self.assertRaises(ValidationError, f.clean, None)
        self.assertRaises(ValidationError, f.clean, 'abc')
        self.assertRaises(ValidationError, f.clean, 123)
        self.assertEqual([], f.clean([]))
        self.assertEqual(['foo', 'bar'], f.clean(['foo', 'bar']))
        self.assertEqual(['foo', 'bar', '$', 'eek'], f.clean(['foo', 'bar', '$', 'eek']))
        self.assertEqual(f.default, list)

    def test_arrayfield_2(self):
        f = ArrayField(null=True)
        self.assertEqual(None, f.clean(None))
        self.assertRaises(ValidationError, f.clean, 'abc')
        self.assertRaises(ValidationError, f.clean, 123)
        self.assertEqual([], f.clean([]))
        self.assertEqual(['foo', 'bar'], f.clean(['foo', 'bar']))
        self.assertEqual(['foo', 'bar', '$', 'eek'], f.clean(['foo', 'bar', '$', 'eek']))

    # TypedArrayField #########################################################

    def test_typedarrayfield_1(self):
        f = TypedArrayField(IntegerField())
        self.assertRaises(ValidationError, f.clean, None)
        self.assertRaises(ValidationError, f.clean, 'abc')
        self.assertRaises(ValidationError, f.clean, 123)
        self.assertEqual([], f.clean([]))
        self.assertRaises(ValidationError, f.clean, ['foo', 'bar'])
        self.assertEqual([1, 2, 3], f.clean([1, 2, 3]))
        self.assertEqual(f.default, list)

    def test_typedarrayfield_2(self):
        f = TypedArrayField(IntegerField(), null=True)
        self.assertEqual(None, f.clean(None))
        self.assertRaises(ValidationError, f.clean, 'abc')
        self.assertRaises(ValidationError, f.clean, 123)
        self.assertEqual([], f.clean([]))
        self.assertRaises(ValidationError, f.clean, ['foo', 'bar'])
        self.assertEqual([1, 2, 3], f.clean([1, 2, 3]))
