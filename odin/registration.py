# -*- coding: utf-8 -*-
from odin.exceptions import RegistrationException


class ResourceCache(object):
    # Use the Borg pattern to share state between all instances. Details at
    # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66531.
    __shared_state = dict(
        resources={}
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
                raise RegistrationException("This resource %r has already been registered" % resource)

            resource_name = resource._meta.resource_name.lower()
            self.resources[resource_name] = resource
            if resource_name != resource._meta.class_name:
                self.resources[resource._meta.class_name] = resource


cache = ResourceCache()

get_resource = cache.get_resource
register_resources = cache.register_resources
