# -*- coding: utf-8 -*-
from copy import deepcopy
import pytest
import datetime
from odin.fields import *
from odin.fields import Field, TimeStampField, NOT_PROVIDED
from odin.datetimeutil import utc, FixedTimezone
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


class FieldTest(Field):
    def to_python(self, value):
        return value


class TestDynamicTypeNameField(IntegerField):
    @staticmethod
    def data_type_name(instance):
        return "Foo"


class TestField(object):
    def test_error_messages_no_overrides(self):
        target = FieldTest()

        assert {
            'invalid_choice': 'Value %r is not a valid choice.',
            'null': 'This field cannot be null.',
            'required': 'This field is required.',
        } == target.error_messages

    def test_error_messages_override_add(self):
        target = FieldTest(error_messages={
            'null': 'Override',
            'other': 'Other Value',
        })

        assert {
            'invalid_choice': 'Value %r is not a valid choice.',
            'null': 'Override',
            'required': 'This field is required.',
            'other': 'Other Value',
        } == target.error_messages

    def test_set_attributes_from_name(self):
        target = FieldTest()
        target.set_attributes_from_name("test_name")

        assert "test_name" == target.name
        assert "test_name" == target.attname
        assert "test name" == target.verbose_name
        assert "test names" == target.verbose_name_plural

    def test_set_attributes_from_name_with_name(self):
        target = FieldTest(name="init_name")
        target.set_attributes_from_name("test_name")

        assert "init_name" == target.name
        assert "test_name" == target.attname
        assert "init name" == target.verbose_name
        assert "init names" == target.verbose_name_plural

    def test_set_attributes_from_name_with_verbose_name(self):
        target = FieldTest(verbose_name="init Verbose Name")
        target.set_attributes_from_name("test_name")

        assert "test_name" == target.name
        assert "test_name" == target.attname
        assert "init Verbose Name" == target.verbose_name
        assert "init Verbose Names" == target.verbose_name_plural

    def test_has_default(self):
        target = FieldTest()

        assert not target.has_default()

    def test_has_default_supplied(self):
        target = FieldTest(default="123")

        assert target.has_default()

    def test_get_default(self):
        target = FieldTest()

        assert target.get_default() is None

    def test_get_default_supplied(self):
        target = FieldTest(default="123")

        assert "123" == target.get_default()

    def test_get_default_callable(self):
        target = FieldTest(default=lambda: "321")

        assert "321" == target.get_default()

    def test_value_from_object(self):
        target = FieldTest()
        target.set_attributes_from_name("test_name")

        an_obj = ObjectValue()
        setattr(an_obj, "test_name", "test_value")

        actual = target.value_from_object(an_obj)
        assert "test_value" == actual

    def test__repr(self):
        target = Field()
        assert "<odin.fields.Field>" == repr(target)
        target.set_attributes_from_name("eek")
        assert "<odin.fields.Field: eek>" == repr(target)

    def test__deep_copy(self):
        field = FieldTest(name="Test")
        target_copy = deepcopy(field)
        target_assign = field
        assert field is target_assign
        assert field is not target_copy
        assert field.name == target_copy.name

    def test_run_validators_and_override_validator_message(self):
        target = FieldTest(error_messages={'test_code': 'Override message'}, validators=[TestValidator(True)])

        try:
            target.run_validators("Placeholder")
        except ValidationError as ve:
            assert 'Override message' == ve.messages[0]
        else:
            raise AssertionError("Validation Error not raised.")

    def test_run_validators_and_override_validator_message_with_params(self):
        target = FieldTest(error_messages={'test_code': 'Override message: %s'}, validators=[TestValidator(True, "123")])

        try:
            target.run_validators("Placeholder")
        except ValidationError as ve:
            assert ['Override message: 123'] == ve.messages
        else:
            raise AssertionError("Validation Error not raised.")

    def test_default_to_python_raises_not_implemented(self):
        target = Field()
        pytest.raises(NotImplementedError, target.to_python, "Anything...")

    def test_clean_uses_default_if_value_is_not_provided_is_true(self):
        target = FieldTest(use_default_if_not_provided=True, default='foo')
        actual = target.clean(NOT_PROVIDED)
        assert 'foo' == actual

    def test_clean_uses_default_if_value_is_not_provided_is_false(self):
        # Need to allow None as the if use_default_if_not_provided is false NOT_PROVIDED evaluates to None.
        target = FieldTest(use_default_if_not_provided=False, default='foo', null=True)
        actual = target.clean(NOT_PROVIDED)
        assert actual is None


class VirtualFieldTest(VirtualField):
    pass


class TestVirtualField(object):
    def test_creation_counter(self):
        current_count = VirtualField.creation_counter
        next_count = current_count + 1
        target = VirtualField()

        assert VirtualField.creation_counter == next_count
        assert target.creation_counter == current_count
        assert hash(target) == current_count

    def test_repr(self):
        target = VirtualFieldTest()
        assert "<tests.test_fields.VirtualFieldTest>" == repr(target)
        target.set_attributes_from_name("eek")
        assert "<tests.test_fields.VirtualFieldTest: eek>" == repr(target)

    def test_default_descriptor_behaviour(self):
        class TestObj(object):
            test_field = VirtualField()
        target = TestObj()

        with pytest.raises(NotImplementedError):
            _ = target.test_field

        with pytest.raises(AttributeError) as excinfo:
            target.test_field = 123

        assert "Read only" == str(excinfo.value)


class TestFields(object):
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
        pytest.raises(ValidationError, f.clean, None)
        pytest.raises(ValidationError, f.clean, '')
        assert f.clean(True)
        assert f.clean(1)
        assert f.clean('Yes')
        assert f.clean('true')
        assert f.clean('T')
        assert f.clean('1')
        pytest.raises(ValidationError, f.clean, 'Awesome!')
        assert not f.clean(False)
        assert not f.clean(0)
        assert not f.clean('No')
        assert not f.clean('false')
        assert not f.clean('F')
        assert not f.clean('0')

    # StringField #############################################################

    def test_stringfield_1(self):
        f = StringField()
        assert '1' == f.clean('1')
        assert 'eek' == f.clean('eek')
        pytest.raises(ValidationError, f.clean, None)
        assert '[1, 2, 3]', f.clean([1, 2 == 3])
        assert f.max_length == None
        self.assertValidatorNotIn(MaxLengthValidator, f.validators)

    def test_stringfield_2(self):
        f = StringField(null=True)
        assert '1' == f.clean('1')
        assert 'eek' == f.clean('eek')
        assert None == f.clean(None)
        assert '[1, 2, 3]', f.clean([1, 2 == 3])
        assert f.max_length == None
        self.assertValidatorNotIn(MaxLengthValidator, f.validators)

    def test_stringfield_3(self):
        f = StringField(null=True, max_length=10)
        assert None == f.clean(None)
        assert '' == f.clean('')
        assert '12345' == f.clean('12345')
        assert '1234567890' == f.clean('1234567890')
        pytest.raises(ValidationError, f.clean, '1234567890a')
        assert f.max_length == 10
        self.assertValidatorIn(MaxLengthValidator, f.validators)

    # URLField ################################################################

    def test_urlfield_1(self):
        f = UrlField()
        assert 'http://www.github.com' == f.clean('http://www.github.com')
        pytest.raises(ValidationError, f.clean, 'eek')
        pytest.raises(ValidationError, f.clean, None)
        assert f.max_length == None
        self.assertValidatorIn(RegexValidator, f.validators)

    # IntegerField ############################################################

    def test_integerfield_1(self):
        f = IntegerField()
        pytest.raises(ValidationError, f.clean, None)
        pytest.raises(ValidationError, f.clean, 'abc')
        assert 123 == f.clean(123)
        assert 123 == f.clean('123')
        assert 123 == f.clean(123.5)
        assert None == f.min_value
        self.assertValidatorNotIn(MinValueValidator, f.validators)
        assert None == f.max_value
        self.assertValidatorNotIn(MaxValueValidator, f.validators)

    def test_integerfield_2(self):
        f = IntegerField(null=True)
        assert None == f.clean(None)
        pytest.raises(ValidationError, f.clean, 'abc')
        assert 69 == f.clean(69)
        assert 69 == f.clean('69')
        assert 69 == f.clean(69.5)
        assert None == f.min_value
        self.assertValidatorNotIn(MinValueValidator, f.validators)
        assert None == f.max_value
        self.assertValidatorNotIn(MaxValueValidator, f.validators)

    def test_integerfield_3(self):
        f = IntegerField(min_value=50, max_value=100)
        pytest.raises(ValidationError, f.clean, None)
        pytest.raises(ValidationError, f.clean, 'abc')
        assert 69 == f.clean(69)
        assert 69 == f.clean('69')
        assert 69 == f.clean(69.5)
        assert 50 == f.clean(50)
        assert 100 == f.clean(100)
        pytest.raises(ValidationError, f.clean, 30)
        pytest.raises(ValidationError, f.clean, 110)
        assert 50 == f.min_value
        self.assertValidatorIn(MinValueValidator, f.validators)
        assert 100 == f.max_value
        self.assertValidatorIn(MaxValueValidator, f.validators)

    # FloatField ##############################################################

    def test_floatfield_1(self):
        f = FloatField()
        pytest.raises(ValidationError, f.clean, None)
        pytest.raises(ValidationError, f.clean, 'abc')
        assert 123 == f.clean(123)
        assert 123.5 == f.clean('123.5')
        assert 123.5 == f.clean(123.5)
        assert None == f.min_value
        self.assertValidatorNotIn(MinValueValidator, f.validators)
        assert None == f.max_value
        self.assertValidatorNotIn(MaxValueValidator, f.validators)

    def test_floatfield_2(self):
        f = FloatField(null=True)
        assert None == f.clean(None)
        pytest.raises(ValidationError, f.clean, 'abc')
        assert 69 == f.clean(69)
        assert 69.5 == f.clean('69.5')
        assert 69.5 == f.clean(69.5)
        assert None == f.min_value
        self.assertValidatorNotIn(MinValueValidator, f.validators)
        assert None == f.max_value
        self.assertValidatorNotIn(MaxValueValidator, f.validators)

    def test_floatfield_3(self):
        f = FloatField(min_value=50.5, max_value=100.4)
        pytest.raises(ValidationError, f.clean, None)
        pytest.raises(ValidationError, f.clean, 'abc')
        assert 69 == f.clean(69)
        assert 69.5 == f.clean('69.5')
        assert 69.5 == f.clean(69.5)
        assert 50.5 == f.clean(50.5)
        assert 100.4 == f.clean(100.4)
        pytest.raises(ValidationError, f.clean, 30)
        pytest.raises(ValidationError, f.clean, 110)
        assert 50.5 == f.min_value
        self.assertValidatorIn(MinValueValidator, f.validators)
        assert 100.4 == f.max_value
        self.assertValidatorIn(MaxValueValidator, f.validators)

    # DateField ###############################################################

    def test_datefield_1(self):
        f = DateField()
        pytest.raises(ValidationError, f.clean, None)
        pytest.raises(ValidationError, f.clean, 'abc')
        pytest.raises(ValidationError, f.clean, 123)
        assert datetime.date(2013, 11, 24) == f.clean('2013-11-24')
        assert datetime.date(2013, 11, 24) == f.clean(datetime.date(2013, 11, 24))
        assert datetime.date(2013, 11, 24) == f.clean(datetime.datetime(2013, 11, 24, 1, 14))

    def test_datefield_2(self):
        f = DateField(null=True)
        assert None == f.clean(None)
        pytest.raises(ValidationError, f.clean, 'abc')
        pytest.raises(ValidationError, f.clean, 123)
        assert datetime.date(2013, 11, 24) == f.clean('2013-11-24')
        assert datetime.date(2013, 11, 24) == f.clean(datetime.date(2013, 11, 24))
        assert datetime.date(2013, 11, 24) == f.clean(datetime.datetime(2013, 11, 24, 1, 14))

    # TimeField ###############################################################

    def test_timefield_1(self):
        f = TimeField(assume_local=False)
        pytest.raises(ValidationError, f.clean, None)
        pytest.raises(ValidationError, f.clean, 'abc')
        pytest.raises(ValidationError, f.clean, 123)
        assert datetime.time(18, 43, tzinfo=utc) == f.clean('18:43:00.000Z')
        assert datetime.time(18, 43, tzinfo=utc) == f.clean(datetime.time(18, 43, tzinfo=utc))

    def test_timefield_2(self):
        f = TimeField(assume_local=False, null=True)
        assert None == f.clean(None)
        pytest.raises(ValidationError, f.clean, 'abc')
        pytest.raises(ValidationError, f.clean, 123)
        assert datetime.time(18, 43, tzinfo=utc) == f.clean('18:43:00.000Z')
        assert datetime.time(18, 43, tzinfo=utc) == f.clean(datetime.time(18, 43, tzinfo=utc))

    # DateTimeField ###########################################################

    def test_datetimefield_1(self):
        f = DateTimeField(assume_local=False)
        pytest.raises(ValidationError, f.clean, None)
        pytest.raises(ValidationError, f.clean, 'abc')
        pytest.raises(ValidationError, f.clean, 123)
        assert datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc) == f.clean('2013-11-24T18:43:00.000Z')
        assert datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc) == f.clean('2013-11-24 18:43:00.000Z')
        assert datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc) == f.clean(datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc))

    def test_datetimefield_2(self):
        f = DateTimeField(assume_local=False, null=True)
        assert None == f.clean(None)
        pytest.raises(ValidationError, f.clean, 'abc')
        pytest.raises(ValidationError, f.clean, 123)
        assert datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc) == f.clean('2013-11-24T18:43:00.000Z')
        assert datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc) == f.clean('2013-11-24 18:43:00.000Z')
        assert datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc) == f.clean(datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc))

    # HttpDateTimeField #######################################################

    def test_httpdatetimefield_1(self):
        f = HttpDateTimeField()
        pytest.raises(ValidationError, f.clean, None)
        pytest.raises(ValidationError, f.clean, 'abc')
        pytest.raises(ValidationError, f.clean, 123)
        assert datetime.datetime(2012, 8, 29, 17, 12, 58, tzinfo=utc) == f.clean('Wed Aug 29 17:12:58 +0000 2012')
        assert datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc) == f.clean(datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc))

    def test_httpdatetimefield_2(self):
        f = HttpDateTimeField(null=True)
        assert None == f.clean(None)
        pytest.raises(ValidationError, f.clean, 'abc')
        pytest.raises(ValidationError, f.clean, 123)
        assert datetime.datetime(2012, 8, 29, 17, 12, 58, tzinfo=utc) == f.clean('Wed Aug 29 17:12:58 +0000 2012')
        assert datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc) == f.clean(datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc))

    # TimeStampField ##########################################################

    def test_timestampfield_1(self):
        f = TimeStampField()
        pytest.raises(ValidationError, f.clean, None)
        pytest.raises(ValidationError, f.clean, 'abc')
        pytest.raises(ValidationError, f.clean, 'Wed Aug 29 17:12:58 +0000 2012')
        assert datetime.datetime(1970, 1, 1, 0, 2, 3, tzinfo=utc) == f.clean(123)
        assert datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc) == f.clean(datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc))

    def test_timestampfield_2(self):
        f = TimeStampField(null=True)
        assert None == f.clean(None)
        pytest.raises(ValidationError, f.clean, 'abc')
        pytest.raises(ValidationError, f.clean, 'Wed Aug 29 17:12:58 +0000 2012')
        assert datetime.datetime(1970, 1, 1, 0, 2, 3, tzinfo=utc) == f.clean(123)
        assert datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc) == f.clean(datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc))

    def test_timestampfield_3(self):
        f = TimeStampField()
        assert None == f.prepare(None)
        assert 123 == f.prepare(datetime.datetime(1970, 1, 1, 0, 2, 3, tzinfo=utc))
        assert 123 == f.prepare(123)
        assert 123 == f.prepare(
            datetime.datetime(1970, 1, 1, 10, 2, 3, tzinfo=FixedTimezone.from_hours_minutes(10)))

    # DictField ###############################################################

    def test_dictfield_1(self):
        f = DictField()
        pytest.raises(ValidationError, f.clean, None)
        pytest.raises(ValidationError, f.clean, 'abc')
        pytest.raises(ValidationError, f.clean, 123)
        assert {} == f.clean({})
        assert {'foo': 'bar'} == f.clean({'foo': 'bar'})
        assert f.default == dict

    def test_dictfield_2(self):
        f = DictField(null=True)
        assert None == f.clean(None)
        assert {} == f.clean({})
        pytest.raises(ValidationError, f.clean, 'abc')
        pytest.raises(ValidationError, f.clean, 123)
        assert {'foo': 'bar'} == f.clean({'foo': 'bar'})

    # ArrayField ##############################################################

    def test_arrayfield_1(self):
        f = ArrayField()
        pytest.raises(ValidationError, f.clean, None)
        pytest.raises(ValidationError, f.clean, 'abc')
        pytest.raises(ValidationError, f.clean, 123)
        assert [] == f.clean([])
        assert ['foo', 'bar'], f.clean(['foo' == 'bar'])
        assert ['foo', 'bar', '$', 'eek'], f.clean(['foo', 'bar', '$' == 'eek'])
        assert f.default == list

    def test_arrayfield_2(self):
        f = ArrayField(null=True)
        assert None == f.clean(None)
        pytest.raises(ValidationError, f.clean, 'abc')
        pytest.raises(ValidationError, f.clean, 123)
        assert [] == f.clean([])
        assert ['foo', 'bar'], f.clean(['foo' == 'bar'])
        assert ['foo', 'bar', '$', 'eek'], f.clean(['foo', 'bar', '$' == 'eek'])

    # TypedListField #########################################################

    def test_typedlistfield_1(self):
        f = TypedListField(IntegerField())
        assert "List<Integer>" == f.data_type_name(f)
        pytest.raises(ValidationError, f.clean, None)
        pytest.raises(ValidationError, f.clean, 'abc')
        pytest.raises(ValidationError, f.clean, 123)
        assert [] == f.clean([])
        pytest.raises(ValidationError, f.clean, ['foo', 'bar'])
        assert [1, 2, 3], f.clean([1, 2 == 3])
        assert f.default == list

    def test_typedlistfield_2(self):
        f = TypedListField(IntegerField(), null=True)
        assert "List<Integer>" == f.data_type_name(f)
        assert None == f.clean(None)
        pytest.raises(ValidationError, f.clean, 'abc')
        pytest.raises(ValidationError, f.clean, 123)
        assert [] == f.clean([])
        pytest.raises(ValidationError, f.clean, ['foo', 'bar'])
        assert [1, 2, 3], f.clean([1, 2 == 3])

    def test_typed_list_field_dynamic_type_name(self):
        f = TypedListField(TestDynamicTypeNameField(), null=True)
        assert "List<Foo>" == f.data_type_name(f)

    # TypedDictField ##########################################################

    def test_typeddictfield_1(self):
        f = TypedDictField(IntegerField())
        assert "Dict<String, Integer>" == f.data_type_name(f)
        pytest.raises(ValidationError, f.clean, None)
        pytest.raises(ValidationError, f.clean, 'abc')
        pytest.raises(ValidationError, f.clean, 123)
        assert {} == f.clean({})
        pytest.raises(ValidationError, f.clean, {'foo': 'bar'})
        assert {'foo': 1} == f.clean({'foo': 1})

    def test_typeddictfield_2(self):
        f = TypedDictField(IntegerField(), null=True)
        assert "Dict<String, Integer>" == f.data_type_name(f)
        assert None == f.clean(None)
        pytest.raises(ValidationError, f.clean, 'abc')
        pytest.raises(ValidationError, f.clean, 123)
        assert {} == f.clean({})
        pytest.raises(ValidationError, f.clean, {'foo': 'bar'})
        assert {'foo': 1} == f.clean({'foo': 1})

    def test_typeddictfield_3(self):
        f = TypedDictField(StringField(), IntegerField(), null=True)
        assert "Dict<Integer, String>" == f.data_type_name(f)
        pytest.raises(ValidationError, f.clean, {'foo': 'bar'})
        assert {1: 'foo'} == f.clean({1: 'foo'})

    def test_typeddictfield_nested_typed_array(self):
        f = TypedDictField(TypedArrayField(StringField()))
        assert "Dict<String, List<String>>" == f.data_type_name(f)
        assert {} == f.clean({})
        pytest.raises(ValidationError, f.clean, {'foo': 'bar'})
        assert {'foo': ['bar', 'eek']}, f.clean({'foo': ['bar' == 'eek']})

    def test_typeddictfield_validate(self):
        f = TypedDictField(
            IntegerField(min_value=5),
            StringField(max_length=5, choices=[
                ('foo', 'Foo'),
                ('bad_value', 'Bad Value'),
            ])
        )
        assert "Dict<String, Integer>" == f.data_type_name(f)
        pytest.raises(ValidationError, f.clean, {None: 6})
        pytest.raises(ValidationError, f.clean, {'bad_value': 6})
        pytest.raises(ValidationError, f.clean, {'bar': 6})
        pytest.raises(ValidationError, f.clean, {'foo': None})
        pytest.raises(ValidationError, f.clean, {'foo': 2})

    def test_typed_dict_field_dynamic_type_name(self):
        f = TypedDictField(
            TestDynamicTypeNameField(),
            TestDynamicTypeNameField(),
        )
        assert "Dict<Foo, Foo>" == f.data_type_name(f)

