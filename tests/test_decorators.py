# -*- coding: utf-8 -*-
import pytest
from odin import decorators
from odin.codecs import json_codec
from odin.exceptions import ValidationError
from .resources import Author


class TestDecorators(object):
    def test_returns_resource(self):
        @decorators.returns_resource(resource=Author)
        def test():
            return {"name": "Foo"}
        target = test()
        assert "Foo" == target.name

    def test_returns_resource_full_clean(self):
        @decorators.returns_resource(resource=Author)
        def test_full_clean():
            return {"name": None}

        @decorators.returns_resource(resource=Author, full_clean=False)
        def test_unclean():
            return {"name": None}

        with pytest.raises(ValidationError):
            test_full_clean()

        target = test_unclean()
        assert target.name is None

    def test_returns_resource_with_codec(self):
        @decorators.returns_resource(resource=Author, codec=json_codec)
        def test():
            return '{"name": "Foo"}'

        target = test()
        assert "Foo" == target.name
