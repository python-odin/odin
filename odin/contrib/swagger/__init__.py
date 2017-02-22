"""
Tools for generating Swagger Specification from resources.
"""
from odin.utils import getmeta
from odin import fields

SWAGGER_SPEC_TYPE_MAPPING = {
    fields.IntegerField: 'integer',
    fields.FloatField: 'number',
    fields.BooleanField: 'boolean',
}
"""
Mapping of fields to Swagger types.
"""

SWAGGER_SPEC_FORMAT_MAPPING = {
    fields.StringField: '',
    fields.IntegerField: 'int64',
    fields.FloatField: 'float',
    fields.BooleanField: '',
    fields.DateField: 'date',
    fields.DateTimeField: 'date-time',
    fields.NaiveTimeField: 'date-time',
}
"""
Mapping of fields to Swagger formats.
"""


def generate_definition(resource):
    """
    Generate a `Swagger Definitions Object <http://swagger.io/specification/#definitionsObject>`_
    from a resource.

    """
    meta = getmeta(resource)

    definition = {
        'type': "object",
        'properties': {}
    }

    for field in meta.all_fields:
        field_definition = {
            'type': SWAGGER_SPEC_TYPE_MAPPING.get(field, 'string')
        }

        if field in SWAGGER_SPEC_FORMAT_MAPPING:
            field_definition['format'] = SWAGGER_SPEC_FORMAT_MAPPING[field]

        if field.doc_text:
            field_definition['description'] = field.doc_text

        definition['properties'][field.name] = field_definition

    return {meta.name: definition}
