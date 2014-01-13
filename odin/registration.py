# -*- coding: utf-8 -*-


def generate_mapping_cache_name(from_resource, to_resource):
    return "%s.%s > %s.%s" % (
        from_resource.__module__, from_resource.__name__,
        to_resource.__module__, to_resource.__name__,
    )


class ResourceCache(object):
    # Use the Borg pattern to share state between all instances. Details at
    # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66531.
    __shared_state = dict(
        resources={},
        mappings={},
    )

    def __init__(self):
        self.__dict__ = self.__shared_state

    def get_resource(self, resource_name):
        """
        Get a resource by name.
        """
        return self.resources.get(resource_name.lower())

    def register_resources(self, *resources):
        """
        Register a resource (or resources)
        """
        for resource in resources:
            resource_name = resource._meta.resource_name.lower()
            self.resources[resource_name] = resource
            if resource_name != resource._meta.class_name:
                self.resources[resource._meta.class_name] = resource

    def get_mapping(self, from_resource, to_resource):
        """
        Get a mapping based on the from and to resources
        """
        mapping_name = generate_mapping_cache_name(from_resource, to_resource)
        return self.mappings[mapping_name]

    def register_mappings(self, *mappings):
        """
        Register a mapping (or mappings)
        """
        for mapping in mappings:
            mapping_name = generate_mapping_cache_name(mapping.from_resource, mapping.to_resource)
            self.mappings[mapping_name] = mapping


cache = ResourceCache()

get_resource = cache.get_resource
register_resources = cache.register_resources
get_mapping = cache.get_mapping
register_mappings = cache.register_mappings
