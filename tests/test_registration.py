from unittest.mock import Mock

import pytest

import odin
from odin import registration
from odin.registration import (
    ResourceCache,
    generate_mapping_cache_name,
)


class DummyBaseResource(odin.Resource):
    name = odin.StringField()

    class Meta:
        name_space = "dummy"


class DummySubResource(DummyBaseResource):
    title = odin.StringField()

    class Meta:
        name_space = "dummy"


class DummyAnotherSubResource(DummyBaseResource):
    count = odin.IntegerField()

    class Meta:
        name_space = "dummy"


class DummyFromResource(odin.Resource):
    value = odin.StringField()


class DummyToResource(odin.Resource):
    value = odin.StringField()


class BaseType:
    pass


class SubType(BaseType):
    pass


class CustomError(Exception):
    pass


class AnotherError(Exception):
    pass


class TestGenerateMappingCacheName:
    def test_generate_mapping_cache_name__with_standard_classes(self):
        # Arrange
        from_obj = DummyFromResource
        to_obj = DummyToResource

        # Act
        result = generate_mapping_cache_name(from_obj, to_obj)

        # Assert
        assert (
            result
            == f"{DummyFromResource.__module__}.DummyFromResource > {DummyToResource.__module__}.DummyToResource"
        )

    def test_generate_mapping_cache_name__with_objects_missing_module_or_name(self):
        # Arrange
        from_obj = "from_string"
        to_obj = 123

        # Act
        result = generate_mapping_cache_name(from_obj, to_obj)

        # Assert
        assert result == ".from_string > .123"


class TestResourceCache:
    def test_init__shared_mode_shares_state(self):
        # Arrange & Act
        cache1 = ResourceCache(shared=True)
        cache2 = ResourceCache(shared=True)
        cache1.resources["test_key"] = DummyBaseResource

        # Assert
        assert "test_key" in cache2.resources

        # Cleanup
        cache1.resources.pop("test_key", None)

    def test_init__unshared_mode_creates_isolated_instance(self):
        # Arrange & Act
        isolated = ResourceCache(shared=False)
        shared = ResourceCache(shared=True)
        isolated.register_resources(DummyBaseResource)

        # Assert
        assert isolated.get_resource("dummy.dummybaseresource") is DummyBaseResource
        assert "dummy.dummybaseresource" not in isolated.mappings
        assert isolated.resources is not shared.resources

    def test_clear__resets_all_cached_state(self):
        # Arrange
        cache = ResourceCache(shared=False)
        cache.register_resources(DummyBaseResource)
        cache.register_field_resolver(Mock(), BaseType)
        cache.register_validation_error_handler(CustomError, Mock())
        _ = cache.get_validation_error_list()
        _ = cache.get_child_resources(DummyBaseResource)

        # Act
        cache.clear()

        # Assert
        assert cache.resources == {}
        assert cache.resource_subclasses == {}
        assert cache.mappings == {}
        assert cache.field_resolvers == []
        assert cache.validation_error_handlers == {}
        assert cache._validation_error_list is None

    def test_register_resources__registers_by_resource_name_and_class_name(self):
        # Arrange
        cache = ResourceCache(shared=False)
        expected_class_name = (
            f"{DummyBaseResource.__module__.lower()}.dummybaseresource"
        )

        # Act
        cache.register_resources(DummyBaseResource)

        # Assert
        assert cache.get_resource("dummy.dummybaseresource") is DummyBaseResource
        assert cache.get_resource(expected_class_name) is DummyBaseResource
        assert cache.get_resource("DUMMY.DUMMYBASERESOURCE") is DummyBaseResource

    def test_get_resource__when_not_registered(self):
        # Arrange
        cache = ResourceCache(shared=False)

        # Act
        result = cache.get_resource("non_existent")

        # Assert
        assert result is None

    def test_get_child_resources__returns_registered_subclasses(self):
        # Arrange
        cache = ResourceCache(shared=False)
        cache.register_resources(DummyBaseResource, DummySubResource)

        # Act
        children = cache.get_child_resources(DummyBaseResource)

        # Assert
        assert children == {DummyBaseResource, DummySubResource}

    def test_get_child_resources__invalidates_cache_on_new_registration(self):
        # Arrange
        cache = ResourceCache(shared=False)
        cache.register_resources(DummyBaseResource, DummySubResource)
        initial_children = cache.get_child_resources(DummyBaseResource)
        assert initial_children == {DummyBaseResource, DummySubResource}

        # Act - register an additional subclass
        cache.register_resources(DummyAnotherSubResource)
        updated_children = cache.get_child_resources(DummyBaseResource)

        # Assert - cache was invalidated and now includes the new subclass
        assert updated_children == {
            DummyBaseResource,
            DummySubResource,
            DummyAnotherSubResource,
        }

    def test_register_and_get_mapping__by_tuple_and_string_key(self):
        # Arrange
        cache = ResourceCache(shared=False)
        mock_mapping = Mock()
        mock_mapping.from_obj = DummyFromResource
        mock_mapping.to_obj = DummyToResource

        # Act
        cache.register_mapping(mock_mapping)
        result_by_tuple = cache.get_mapping(DummyFromResource, DummyToResource)

        # Assert
        assert result_by_tuple is mock_mapping

    def test_get_mapping__when_not_found_raises_key_error(self):
        # Arrange
        cache = ResourceCache(shared=False)

        # Act & Assert
        with pytest.raises(KeyError):
            cache.get_mapping(DummyFromResource, DummyToResource)

    def test_register_and_get_field_resolver__basic_resolution(self):
        # Arrange
        cache = ResourceCache(shared=False)
        mock_resolver = Mock(return_value="resolved")
        cache.register_field_resolver(mock_resolver, BaseType)

        # Act
        result = cache.get_field_resolver(BaseType)

        # Assert
        assert result == "resolved"
        mock_resolver.assert_called_once_with(BaseType)

    def test_get_field_resolver__resolves_subclass(self):
        # Arrange
        cache = ResourceCache(shared=False)
        mock_resolver = Mock(return_value="resolved_base")
        cache.register_field_resolver(mock_resolver, BaseType)

        # Act
        result = cache.get_field_resolver(SubType)

        # Assert
        assert result == "resolved_base"
        mock_resolver.assert_called_once_with(SubType)

    def test_get_field_resolver__subclass_resolver_precedence_over_base_resolver(self):
        # Arrange - register base resolver first, then subclass resolver
        cache = ResourceCache(shared=False)
        base_resolver = Mock(return_value="base_resolved")
        sub_resolver = Mock(return_value="sub_resolved")

        cache.register_field_resolver(base_resolver, BaseType)
        cache.register_field_resolver(sub_resolver, SubType)

        # Act
        result = cache.get_field_resolver(SubType)

        # Assert - SubType resolver takes precedence over BaseType resolver
        assert result == "sub_resolved"
        sub_resolver.assert_called_once_with(SubType)
        base_resolver.assert_not_called()

    def test_get_field_resolver__subclass_resolver_precedence_regardless_of_registration_order(
        self,
    ):
        # Arrange - register subclass resolver first, then base resolver
        cache = ResourceCache(shared=False)
        base_resolver = Mock(return_value="base_resolved")
        sub_resolver = Mock(return_value="sub_resolved")

        cache.register_field_resolver(sub_resolver, SubType)
        cache.register_field_resolver(base_resolver, BaseType)

        # Act
        result = cache.get_field_resolver(SubType)

        # Assert - SubType resolver still takes precedence due to MRO depth ordering
        assert result == "sub_resolved"
        sub_resolver.assert_called_once_with(SubType)
        base_resolver.assert_not_called()

    def test_get_field_resolver__when_not_found_raises_key_error(self):
        # Arrange
        cache = ResourceCache(shared=False)

        # Act & Assert
        with pytest.raises(KeyError, match="No field resolver could be found"):
            cache.get_field_resolver(int)

    def test_validation_error_handlers__registration_and_lookup(self):
        # Arrange
        cache = ResourceCache(shared=False)
        mock_handler = Mock()
        cache.register_validation_error_handler(CustomError, mock_handler)

        # Act
        error_list = cache.get_validation_error_list()
        handler_from_instance = cache.get_validation_error_handler(CustomError("test"))
        handler_from_class = cache.get_validation_error_handler(CustomError)

        # Assert
        assert error_list == (CustomError,)
        assert handler_from_instance is mock_handler
        assert handler_from_class is mock_handler

    def test_validation_error_handlers__invalidates_cached_list_on_new_registration(
        self,
    ):
        # Arrange
        cache = ResourceCache(shared=False)
        cache.register_validation_error_handler(CustomError, Mock())
        initial_list = cache.get_validation_error_list()
        assert initial_list == (CustomError,)

        # Act - register another error handler
        cache.register_validation_error_handler(AnotherError, Mock())
        updated_list = cache.get_validation_error_list()

        # Assert - cache was invalidated and now includes the new error class
        assert updated_list == (CustomError, AnotherError)


class TestModuleLevelRegistrationFunctions:
    def test_module_level_aliases_point_to_global_cache(self):
        # Arrange & Act & Assert
        assert registration.register_resources == registration.cache.register_resources
        assert registration.get_resource == registration.cache.get_resource
        assert (
            registration.get_child_resources == registration.cache.get_child_resources
        )
        assert registration.register_mapping == registration.cache.register_mapping
        assert registration.get_mapping == registration.cache.get_mapping
        assert (
            registration.register_field_resolver
            == registration.cache.register_field_resolver
        )
        assert registration.get_field_resolver == registration.cache.get_field_resolver
        assert (
            registration.register_validation_error_handler
            == registration.cache.register_validation_error_handler
        )
        assert (
            registration.get_validation_error_list
            == registration.cache.get_validation_error_list
        )
        assert (
            registration.get_validation_error_handler
            == registration.cache.get_validation_error_handler
        )
