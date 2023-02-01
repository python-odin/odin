import abc


class ResourceIterable(abc.ABC):
    """Iterable object that yields resources."""

    @abc.abstractmethod
    def __iter__(self):
        """Iterate resources"""


class TypedResourceIterable(ResourceIterable, abc.ABC):
    """Iterable object that yields a specific resource."""

    def __init__(self, resource_type):
        self.resource_type = resource_type
