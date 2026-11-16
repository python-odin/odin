from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from odin.utils import getmeta

if TYPE_CHECKING:
    from odin.mapping import Mapping

__all__ = (
    "ResourceCache",
    "cache",
    "generate_mapping_cache_name",
    "get_child_resources",
    "get_field_resolver",
    "get_mapping",
    "get_resource",
    "get_validation_error_handler",
    "get_validation_error_list",
    "register_field_resolver",
    "register_mapping",
    "register_resources",
    "register_validation_error_handler",
)


def generate_mapping_cache_name(from_obj: Any, to_obj: Any) -> str:
    """Generate a string cache key for a mapping."""
    from_name = getattr(from_obj, "__name__", str(from_obj))
    from_mod = getattr(from_obj, "__module__", "")
    to_name = getattr(to_obj, "__name__", str(to_obj))
    to_mod = getattr(to_obj, "__module__", "")
    return f"{from_mod}.{from_name} > {to_mod}.{to_name}"


class ResourceCache:
    """Registry and cache for resources, mappings, field resolvers, and error handlers."""

    # Use the Borg pattern to share state between all instances. Details at
    # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66531.
    __shared_state: dict[str, Any] = {
        "resources": {},
        "resource_subclasses": {},
        "mappings": {},
        "field_resolvers": [],
        "validation_error_handlers": {},
        "_validation_error_list": None,
    }

    def __init__(self, shared: bool = True):
        if shared:
            self.__dict__ = self.__shared_state
        else:
            self.resources: dict[str, type] = {}
            self.resource_subclasses: dict[type, set[type]] = {}
            self.mappings: dict[tuple[Any, Any] | str, Any] = {}
            self.field_resolvers: list[tuple[type, Callable]] = []
            self.validation_error_handlers: dict[type[Exception], Callable] = {}
            self._validation_error_list: tuple[type[Exception], ...] | None = None

    def clear(self):
        """Clear all registered items and cached state."""
        self.resources.clear()
        self.resource_subclasses.clear()
        self.mappings.clear()
        self.field_resolvers.clear()
        self.validation_error_handlers.clear()
        self._validation_error_list = None

    def register_resources(self, *resources: type):
        """Register a resource (or resources).

        :param resources: Argument list of resources to register.
        """
        for resource in resources:
            meta = getmeta(resource)
            resource_name = meta.resource_name.lower()
            self.resources[resource_name] = resource
            class_name = meta.class_name.lower()
            if resource_name != class_name:
                self.resources[class_name] = resource

        # Invalidate child resource cache when new resources are registered
        self.resource_subclasses.clear()

    def get_resource(self, resource_name: str) -> type | None:
        """Get a resource by name.

        :param resource_name: Name of the resource to find.
        :returns: The resource type that matches requested name (case insensitive); or :const:`None` if the
            requested name has not been registered.
        """
        return self.resources.get(resource_name.lower())

    def get_child_resources(self, resource: type) -> set[type]:
        """Get subclasses of a resource.

        :param resource: Resource base class.
        :returns: Set of resource types that subclass *resource*.
        """
        resource_subclasses = self.resource_subclasses.get(resource)
        if resource_subclasses is None:
            self.resource_subclasses[resource] = resource_subclasses = {
                child
                for child in self.resources.values()
                if isinstance(child, type) and issubclass(child, resource)
            }
        return resource_subclasses

    def register_mapping(self, mapping: "Mapping"):
        """Register a mapping.

        :param mapping: Mapping object to register.
        """
        key = (mapping.from_obj, mapping.to_obj)
        self.mappings[key] = mapping
        # Keep legacy string key for backward compatibility
        mapping_name = generate_mapping_cache_name(mapping.from_obj, mapping.to_obj)
        self.mappings[mapping_name] = mapping

    def get_mapping(self, from_obj: Any, to_obj: Any) -> "Mapping":
        """Get a mapping based on the from and to objects (likely to be resources).

        :param from_obj: Object to map from.
        :param to_obj: Object to map to.
        :returns: A mapping object that supports mapping from *from_obj* to *to_obj*
        :raises: KeyError if a mapping cannot be found.
        """
        key = (from_obj, to_obj)
        if key in self.mappings:
            return self.mappings[key]
        mapping_name = generate_mapping_cache_name(from_obj, to_obj)
        return self.mappings[mapping_name]

    def register_field_resolver(self, resolver: Callable, base_type: type):
        """Register a field resolver.

        The *base_type* will also cover all subclasses.

        :param resolver: Resolver object used to resolve subclasses of *base_type*.
        :param base_type: Base type for subclasses that this resolver will work with.
        """
        self.field_resolvers = [
            (b, r) for b, r in self.field_resolvers if b is not base_type
        ]
        self.field_resolvers.append((base_type, resolver))
        self.field_resolvers.sort(
            key=lambda item: len(item[0].__mro__) if isinstance(item[0], type) else 0,
            reverse=True,
        )

    def get_field_resolver(self, obj_type: type) -> Any:
        """Get a field resolver for an object type.

        :param obj_type: Object type to find a field resolver for.
        :return: A field resolver instance for resolving fields on *obj_type*.
        :raises: KeyError if a resolver cannot be found.
        """
        for base_type, field_resolver in self.field_resolvers:
            try:
                if issubclass(obj_type, base_type):
                    return field_resolver(obj_type)
            except TypeError:
                if obj_type == base_type:
                    return field_resolver(obj_type)
        msg = f"No field resolver could be found for {obj_type!r}"
        raise KeyError(msg)

    def register_validation_error_handler(
        self, error_type: type[Exception], handler: Callable
    ):
        """Register a validation error handler.

        :param handler: A method that can handle the exception type.
        :param error_type: Error exception to register a handler for.
        """
        self.validation_error_handlers[error_type] = handler
        self._validation_error_list = None

    def get_validation_error_list(self) -> tuple[type[Exception], ...]:
        """Get a list of validation errors that can be used in an exception clause.

        :return: Tuple of error types.
        """
        if self._validation_error_list is None:
            self._validation_error_list = tuple(self.validation_error_handlers.keys())
        return self._validation_error_list

    def get_validation_error_handler(
        self, error_type: Exception | type[Exception]
    ) -> Callable:
        """Get the handler for a particular error_type.

        :param error_type: Error exception related to a handler.
        :return: Handler
        """
        error_cls = error_type if isinstance(error_type, type) else error_type.__class__
        return self.validation_error_handlers[error_cls]


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
