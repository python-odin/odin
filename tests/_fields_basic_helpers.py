# -*- coding: utf-8 -*-
from odin.exceptions import ValidationError


def create_simple_method(obj, method_name, value, expected, num):
    method = obj if method_name is None else getattr(obj, method_name)

    if expected is None:
        name_mask = "test_%s_%s_returns_none_%d"

        def tst_func(self):
            self.assertIsNone(method(value))

    elif isinstance(expected, type) and issubclass(expected, Exception):
        name_mask = "test_%s_%s_raises_error_%d"

        def tst_func(self):
            # assertRaises not used, so as to be able to produce an error message
            # containing the tested value
            try:
                method(value)
            except expected:
                pass
            else:
                self.fail("%s not raised when validating '%s'" % (
                    expected.__name__, value))

    else:
        name_mask = "test_%s_%s_%d"

        def tst_func(self):
            try:
                self.assertEqual(expected, method(value))
            except ValidationError as e:
                self.fail("Validation of '%s' failed. Error message was: %s" % (
                    value, str(e)))

    test_name = name_mask % (obj.__class__.__name__, method_name, num)
    return test_name, tst_func
