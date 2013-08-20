# -*- coding: utf-8 -*-
import unittest
from odin import exceptions


class ValidationException(unittest.TestCase):
    def test_create_with_string(self):
        TEST_MESSAGE = "Test message"
        target = exceptions.ValidationError(TEST_MESSAGE)

        self.assertListEqual([TEST_MESSAGE], target.messages)

    def test_create_with_list(self):
        TEST_MESSAGE_LIST = ["Test message", "Test message 2"]
        target = exceptions.ValidationError(TEST_MESSAGE_LIST)

        self.assertListEqual(TEST_MESSAGE_LIST, target.messages)

    def test_create_with_dict(self):
        TEST_MESSAGE_DICT = {
            "Test Key 1": "Test Message 1",
            "Test Key 2": "Test Message 2",
        }
        target = exceptions.ValidationError(TEST_MESSAGE_DICT)

        self.assertDictEqual(TEST_MESSAGE_DICT, target.message_dict)
