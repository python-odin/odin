class ResourceIterable(object):
    """
    Iterable object that yields resources.
    """
    def __iter__(self):
        raise NotImplementedError()


class TypedResourceIterable(ResourceIterable):
    """
    Iterable object that yields a specific resource.
    """
    def __init__(self, resource_type):
        self.resource_type = resource_type

    def __iter__(self):
        raise NotImplementedError()
