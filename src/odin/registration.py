# -*- coding: utf-8 -*-


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
            resource_name = resource._meta.resource_name.lower()
            if resource_name in self.resources:
                continue

            self.resources[resource_name] = resource

cache = ResourceCache()

get_resource = cache.get_resource
register_resources = cache.register_resources
