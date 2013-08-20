# -*- coding: utf-8 -*-
try:
    import simplejson as json
except ImportError:
    import json
from odin import resources


class JSRNEncoder(json.JSONEncoder):
    """
    Encoder for JSRN resources.
    """
    def default(self, o):
        if isinstance(o, resources.Resource):
            obj = {f.name: f.to_json(f.value_from_object(o)) for f in o._meta.fields}
            obj[resources.RESOURCE_TYPE_FIELD] = o._meta.resource_name
            return obj
        return super(JSRNEncoder, self)


def build_object_graph(obj, resource_name=None):
    """
    From the decoded JSON structure, generate an object graph.

    :raises ValidationError: During building of the object graph and issues discovered are raised as a ValidationError.
    """

    if isinstance(obj, dict):
        return resources.create_resource_from_dict(obj, resource_name)

    if isinstance(obj, list):
        return [build_object_graph(o, resource_name) for o in obj]

    return obj
