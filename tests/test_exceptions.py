# -*- coding: utf-8 -*-
from odin import exceptions


class TestValidationException(object):
    def test_with_string(self):
        test_message = "Test message"
        target = exceptions.ValidationError(test_message)

        assert [test_message] == target.messages
        assert not hasattr(target, 'message_dict')
        assert "['Test message']" == str(target)
        assert "ValidationError(['Test message'])" == repr(target)

    def test_with_list(self):
        test_message_list = ["Test message", "Test message 2"]
        target = exceptions.ValidationError(test_message_list)

        assert test_message_list == target.messages
        assert not hasattr(target, 'message_dict')
        assert "['Test message', 'Test message 2']" == str(target)
        assert "ValidationError(['Test message', 'Test message 2'])" == repr(target)

    def test_with_dict(self):
        test_message_dict = {
            "Test Key 1": ["Test Message 1"],
            "Test Key 2": ["Test Message 2"],
        }
        target = exceptions.ValidationError(test_message_dict)

        assert test_message_dict == target.message_dict
        assert [{
            "Test Key 1": ["Test Message 1"],
            "Test Key 2": ["Test Message 2"],
        }] == target.messages

        expected = {'Test Key 2': ['Test Message 2'], 'Test Key 1': ['Test Message 1']}
        assert expected == target.message_dict
        assert(
            "ValidationError({'Test Key 1': ['Test Message 1'], 'Test Key 2': ['Test Message 2']})" ==
            repr(target)
        )
