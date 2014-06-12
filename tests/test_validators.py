# -*- coding: utf-8 -*-
import unittest
from odin import validators
from odin.exceptions import ValidationError


class ValidatorTestCase(unittest.TestCase):
    def test_regex_validator(self):
        target = validators.RegexValidator(r'^[a-z]{3}$', "Please enter 3 alpha characters.", "match_chars")

        self.assertEqual("Please enter 3 alpha characters.", target.message)
        self.assertEqual("match_chars", target.code)

        target("abc")
        target("cba")
        self.assertRaises(ValidationError, target, "a")
        self.assertRaises(ValidationError, target, "abcd")
        self.assertRaises(ValidationError, target, "123")

    def test_url(self):
        validators.validate_url('http://www.djangoproject.com/')
        validators.validate_url('http://localhost/')
        validators.validate_url('http://example.com/')
        validators.validate_url('http://www.example.com/')
        validators.validate_url('http://www.example.com:8000/test')
        validators.validate_url('http://valid-with-hyphens.com/')
        validators.validate_url('http://subdomain.example.com/')
        validators.validate_url('http://200.8.9.10/')
        validators.validate_url('http://200.8.9.10:8000/test')
        validators.validate_url('http://valid-----hyphens.com/')
        validators.validate_url('http://example.com?something=value')
        validators.validate_url('http://example.com/index.php?something=value&another=value2')
        validators.validate_url('https://example.com/')
        validators.validate_url('ftp://example.com/')
        validators.validate_url('ftps://example.com/')
        validators.validate_url('http://savage.company/')
    
        self.assertRaises(ValidationError, validators.validate_url, 'foo')
        self.assertRaises(ValidationError, validators.validate_url, 'http://')
        self.assertRaises(ValidationError, validators.validate_url, 'http://example')
        self.assertRaises(ValidationError, validators.validate_url, 'http://example.')
        self.assertRaises(ValidationError, validators.validate_url, 'http://.com')
        self.assertRaises(ValidationError, validators.validate_url, 'http://invalid-.com')
        self.assertRaises(ValidationError, validators.validate_url, 'http://-invalid.com')
        self.assertRaises(ValidationError, validators.validate_url, 'http://inv-.alid-.com')
        self.assertRaises(ValidationError, validators.validate_url, 'http://inv-.-alid.com')

    def test_max_value_validator(self):
        target = validators.MaxValueValidator(10)

        target(10)
        target(1)
        target(-10)
        self.assertRaises(ValidationError, target, 11)

    def test_min_value_validator(self):
        target = validators.MinValueValidator(10)

        target(10)
        self.assertRaises(ValidationError, target, 1)
        self.assertRaises(ValidationError, target, -10)
        target(11)

    def test_length_validator(self):
        target = validators.LengthValidator(10)
        target("1234567890")
        self.assertRaises(ValidationError, target, "123456789")
        self.assertRaises(ValidationError, target, "12345678901")

    def test_max_length_validator(self):
        target = validators.MaxLengthValidator(10)

        target("123457890")
        target("12345")
        target("")
        self.assertRaises(ValidationError, target, "12345678901")

    def test_min_length_validator(self):
        target = validators.MinLengthValidator(10)

        self.assertRaises(ValidationError, target, "123457890")
        self.assertRaises(ValidationError, target, "12345")
        self.assertRaises(ValidationError, target, "")
        target("12345678901")


class SimpleValidatorTestCase(unittest.TestCase):
    def test_method(self):
        def reflect(v):
            return v

        validator = validators.simple_validator(reflect)

        self.assertRaises(ValidationError, validator, False)
        validator(True)

    def test_decorator(self):

        @validators.simple_validator()
        def reflect_validator(v):
            return v

        self.assertRaises(ValidationError, reflect_validator, False)
        reflect_validator(True)
