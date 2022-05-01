"""
Tests of polymorphic behaviours
"""
import odin
from odin.resources import create_resource_from_dict


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
