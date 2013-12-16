# -*- coding: utf-8 -*-
import unittest
import sys
from odin import exceptions


class ValidationException(unittest.TestCase):
    def test_with_string(self):
        test_message = "Test message"
        target = exceptions.ValidationError(test_message)

        self.assertListEqual([test_message], target.messages)
        self.assertFalse(hasattr(target, 'message_dict'))
        self.assertEqual("['Test message']", str(target))
        self.assertEqual("ValidationError(['Test message'])", repr(target))

    def test_with_list(self):
        test_message_list = ["Test message", "Test message 2"]
        target = exceptions.ValidationError(test_message_list)

        self.assertListEqual(test_message_list, target.messages)
        self.assertFalse(hasattr(target, 'message_dict'))
        self.assertEqual("['Test message', 'Test message 2']", str(target))
        self.assertEqual("ValidationError(['Test message', 'Test message 2'])", repr(target))

    @unittest.skipIf(sys.version_info[0] > 2 and sys.version_info[1] > 2, "Disabled as Python 3.3 randomises the hash "
                                                                          "function.")
    def test_with_dict(self):
        test_message_dict = {
            "Test Key 1": ["Test Message 1"],
            "Test Key 2": ["Test Message 2"],
        }
        target = exceptions.ValidationError(test_message_dict)

        self.assertDictEqual(test_message_dict, target.message_dict)
        self.assertListEqual([{
            "Test Key 1": ["Test Message 1"],
            "Test Key 2": ["Test Message 2"],
        }], target.messages)
        self.assertEqual("{'Test Key 2': ['Test Message 2'], 'Test Key 1': ['Test Message 1']}", str(target))
        self.assertEqual("ValidationError({'Test Key 2': ['Test Message 2'], 'Test Key 1': ['Test Message 1']})",
                         repr(target))
