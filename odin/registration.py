# -*- coding: utf-8 -*-
from odin.exceptions import RegistrationError


def generate_mapping_cache_name(source, destination):
    return "%s.%s > %s.%s" % (
        source.__module__, source.__name__,
        destination.__module__, destination.__name__,
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

    def __iter__(self):
        """
        Iterate through registered resources.
        """
        return self.resources.itervalues()

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
            if resource in self.resources.values():
                raise RegistrationError("This resource %r has already been registered" % resource)

            resource_name = resource._meta.resource_name.lower()
            self.resources[resource_name] = resource
            if resource_name != resource._meta.class_name:
                self.resources[resource._meta.class_name] = resource

    def get_mapping(self, source, destination):
        mapping_name = generate_mapping_cache_name(source, destination)
        return self.mappings[mapping_name]


    def register_mappings(self, *mappings):
        for mapping in mappings:
            mapping_name = generate_mapping_cache_name(mapping.source, )




cache = ResourceCache()

get_resource = cache.get_resource
register_resources = cache.register_resources
