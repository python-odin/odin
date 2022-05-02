"""
Tests of polymorphic behaviours
"""
import pytest

import odin
from odin.resources import create_resource_from_dict
from odin.utils import getmeta


class AbstractResource(odin.Resource):
    class Meta:
        abstract = True
        namespace = "au.com.example.abstracts"
        type_field = "type"


class ResourceA(AbstractResource):
    class Meta:
        type_field = "type"


class ResourceB(AbstractResource):
    pass


def test_resolve_resource_using_full_type_field():
    actual = create_resource_from_dict(
        {"type": "au.com.example.abstracts.ResourceA"},
        AbstractResource,
        full_clean=False,
    )

    assert isinstance(actual, ResourceA)


def test_resolve_resource_using_partial_type_field():
    actual = create_resource_from_dict(
        {"type": "ResourceB"},
        AbstractResource,
        full_clean=False,
    )

    assert isinstance(actual, ResourceB)


@pytest.mark.parametrize("resource", (ResourceA, ResourceB))
def test_type_field_is_inherited(resource):
    expected = getmeta(AbstractResource).type_field
    actual = getmeta(resource).type_field

    assert actual == expected


@pytest.mark.parametrize("resource", (ResourceA, ResourceB))
def test_name_space_is_inherited(resource):
    expected = getmeta(AbstractResource).name_space
    actual = getmeta(resource).name_space

    assert actual == expected
