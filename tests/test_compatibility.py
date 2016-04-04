# -*- coding: utf-8 -*-
import unittest
import warnings
from odin.compatibility import deprecated


class DeprecatedTestCase(unittest.TestCase):
    def test_add_deprecation_warning(self):
        @deprecated(message="No longer used.")
        def deprecated_function():
            pass

        with warnings.catch_warnings(record=True) as warning_log:
            deprecated_function()

        # Compare the message values
        self.assertListEqual([
            str(m.message) for m in
            sorted(warning_log, key=lambda l: str(l.message))
        ], [
            'deprecated_function is deprecated and scheduled for removal. No longer used.',
        ])
