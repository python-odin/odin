# -*- coding: utf-8 -*-
import warnings
from odin.compatibility import deprecated


class TestDeprecated(object):
    def test_function_deprecation_warning(self):
        @deprecated("No longer used.", category=UserWarning)
        def deprecated_function():
            pass

        with warnings.catch_warnings(record=True) as warning_log:
            deprecated_function()

        # Compare the message values
        assert [
            str(m.message) for m in
            sorted(warning_log, key=lambda l: str(l.message))
        ] == [
            'deprecated_function is deprecated and scheduled for removal. No longer used.',
        ]

    def test_class_deprecation_warning(self):
        @deprecated("No longer used.", category=UserWarning)
        class DeprecatedClass(object):
            pass

        with warnings.catch_warnings(record=True) as warning_log:
            DeprecatedClass()

        # Compare the message values
        assert [
            str(m.message) for m in
            sorted(warning_log, key=lambda l: str(l.message))
        ] == [
            'DeprecatedClass is deprecated and scheduled for removal. No longer used.',
        ]

