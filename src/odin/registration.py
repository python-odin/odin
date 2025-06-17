from collections.abc import Sequence

from odin.utils import getmeta


def generate_mapping_cache_name(from_obj, to_obj):
    return f"{from_obj.__module__}.{from_obj.__name__} > {to_obj.__module__}.{to_obj.__name__}"


class ResourceCache:
    # Use the Borg pattern to share state between all instances. Details at
    # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66531.
    __shared_state = {
        "resources": {},
        "resource_subclasses": {},
        "mappings": {},
        "field_resolvers": set(),
        "validation_error_handlers": {},
    }

    def __init__(self):
        self.__dict__ = self.__shared_state

    def register_resources(self, *resources):
        """
        Register a resource (or resources).

        :param resources: Argument list of resources to register.

        """
        for resource in resources:
            meta = getmeta(resource)
            resource_name = meta.resource_name.lower()
            self.resources[resource_name] = resource
            class_name = meta.class_name.lower()
            if resource_name != class_name:
                self.resources[class_name] = resource

    def get_resource(self, resource_name: str):
        """
        Get a resource by name.

        :param resource_name: Name of the resource to find.
        :returns: The resource type that matches requested name (case insensitive); or :const:`None` if the
            requested name has not been registered.

        """
        return self.resources.get(resource_name.lower())

    def get_child_resources(self, resource: type) -> Sequence[type]:
        """
        Get subclasses of a resource.
        """
        resource_subclasses = self.resource_subclasses.get(resource)
        if resource_subclasses is None:
            self.resource_subclasses[resource] = resource_subclasses = {
                child
                for child in self.resources.values()
                if issubclass(child, resource)
            }
        return resource_subclasses

    def register_mapping(self, mapping):
        """
        Register a mapping

        :param mapping: Mapping object to register.

        """
        mapping_name = generate_mapping_cache_name(mapping.from_obj, mapping.to_obj)
        self.mappings[mapping_name] = mapping

    def get_mapping(self, from_obj, to_obj):
        """
        Get a mapping based on the from and to objects (likely to be resources).

        :param from_obj: Object to map from.
        :param to_obj: Object to map to.
        :returns: A mapping object that supports mapping from *from_obj* to *to_obj*
        :raises: KeyError if a mapping cannot be found.

        """
        mapping_name = generate_mapping_cache_name(from_obj, to_obj)
        return self.mappings[mapping_name]

    def register_field_resolver(self, resolver, base_type):
        """
        Register a field resolver.

        The *base_type* will also cover all subclasses.

        :param base_type: Base type for subclasses that this resolver will work with.
        :param resolver: Resolver object used to resolve subclasses of *base_type*.

        """
        self.field_resolvers.add((base_type, resolver))

    def get_field_resolver(self, obj_type):
        """
        Get a field resolver for an object type.

        :param obj_type: Object type to find a field resolver for.
        :return: A field resolver instance for resolving fields on *obj_type*.
        :raises: KeyError if a resolver cannot be found.

        """
        for base_type, field_resolver in self.field_resolvers:
            if issubclass(obj_type, base_type):
                return field_resolver(obj_type)
        msg = f"No field resolver could be found for {obj_type!r}"
        raise KeyError(msg)

    def register_validation_error_handler(self, error_type, handler):
        """
        Register a validation error handler.

        :param handler: A method that can handle the exception type.
        :param error_type: Error exception to register a handler for.

        """
        self.validation_error_handlers[error_type] = handler

    def get_validation_error_list(self):
        """
        Get a list of validation errors that can be used in an exception clause.

        :return: List of error types.

        """
        try:
            return self._validation_error_list
        except AttributeError:
            validation_error_list = tuple(self.validation_error_handlers.keys())
            self._validation_error_list = validation_error_list
            return validation_error_list

    def get_validation_error_handler(self, error_type):
        """
        Get the handler for a particular error_type.

        :param error_type: Error exception related to a handler.
        :return: Handler

        """
        return self.validation_error_handlers[error_type.__class__]


cache = ResourceCache()

register_resources = cache.register_resources
get_resource = cache.get_resource
get_child_resources = cache.get_child_resources

register_mapping = cache.register_mapping
get_mapping = cache.get_mapping

register_field_resolver = cache.register_field_resolver
get_field_resolver = cache.get_field_resolver

register_validation_error_handler = cache.register_validation_error_handler
get_validation_error_list = cache.get_validation_error_list
get_validation_error_handler = cache.get_validation_error_handler
