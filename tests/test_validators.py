# -*- coding: utf-8 -*-
import unittest
from _fields_basic_helpers import create_simple_method
from odin import validators
from odin.exceptions import ValidationError


VALIDATOR_TESTS = [
    (validators.MaxValueValidator(10), 10, None),
    (validators.MaxValueValidator(10), 1, None),
    (validators.MaxValueValidator(10), 11, ValidationError),

    (validators.MinValueValidator(10), 10, None),
    (validators.MinValueValidator(10), 1, ValidationError),
    (validators.MinValueValidator(10), 11, None),

    (validators.MaxLengthValidator(10), "1234567890", None),
    (validators.MaxLengthValidator(10), "12345", None),
    (validators.MaxLengthValidator(10), "12345678901", ValidationError),

    (validators.MinLengthValidator(10), "1234567890", None),
    (validators.MinLengthValidator(10), "12345", ValidationError),
    (validators.MinLengthValidator(10), "12345678901", None),
]


class ValidatorTestCase(unittest.TestCase):
    pass

for idx, (field, value, expected) in enumerate(VALIDATOR_TESTS):
    name, method = create_simple_method(field, None, value, expected, idx)
    setattr(ValidatorTestCase, name, method)
