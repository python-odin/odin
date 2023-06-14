"""JSON schema support for Odin."""
import json
from typing import Any, Dict, Final, List, Sequence, TextIO, Type, Union

import odin
from odin.registration import get_child_resources
from odin.resources import ResourceBase, ResourceOptions
from odin.utils import getmeta

SCHEMA_DIALECT: Final[str] = "https://json-schema.org/draft/2020-12/schema"


class JSONSchema:
    """JSON Schema representation of an Odin resource."""

    def __init__(
        self, resource: Type[ResourceBase], *, require_type_field: bool = True
    ):
        self.resource = resource
        self.require_type_field = require_type_field

        self.defs = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert the schema to a dictionary."""
        meta = getmeta(self.resource)

        schema = {
            "$schema": SCHEMA_DIALECT,
            "$id": f"urn:jsonschema:{meta.resource_name}",
        }
        schema.update(self._resource_to_schema(meta))
        schema["$defs"] = self.defs

        return schema

    def _resource_to_schema(self, meta: ResourceOptions) -> Dict[str, Any]:
        """Convert a resource to a JSON schema."""
        schema = {
            "type": "object",
            "properties": self._fields_to_properties(meta),
            "required": self._required_fields(meta),
            "additionalProperties": False,
        }
        return schema

    def _required_fields(self, meta: ResourceOptions) -> Sequence[str]:
        """Get a list of required fields."""
        required = [field.name for field in meta.fields if not field.null]
        if self.require_type_field:
            required.append(meta.type_field)
        return required

    def _fields_to_properties(self, meta: ResourceOptions) -> Dict[str, Any]:
        """Convert a set of fields to JSON schema properties."""
        properties = {meta.type_field: {"const": meta.resource_name}}
        for field in meta.fields:
            properties[field.name] = self._field_to_schema(field)
        return properties

    def _field_to_schema(self, field: odin.Field) -> Dict[str, Any]:
        """Convert a field to a JSON schema."""

        if isinstance(field, odin.CompositeField):
            return self._composite_field_to_schema(field)

        schema = {
            "type": self._field_type(field),
            "description": field.doc_text or "",
        }
        if field.choices:
            schema["enum"] = tuple(str(value) for value in field.choice_values)

        return schema

    def _field_type(self, field: odin.Field) -> Union[str, List[str]]:
        """Get the type of a field."""

        if isinstance(field, odin.ListField):
            type_name = "array"
        elif isinstance(field, odin.IntegerField):
            type_name = "integer"
        elif isinstance(field, odin.FloatField):
            type_name = "number"
        elif isinstance(field, odin.BooleanField):
            type_name = "boolean"
        elif isinstance(field, odin.DictField):
            type_name = "object"
        else:
            type_name = "string"

        return [type_name, "null"] if field.null else type_name

    def _composite_field_to_schema(self, field: odin.CompositeField) -> Dict[str, Any]:
        """Convert a composite field to a JSON schema."""

        # Handle abstract resources
        child_resources = get_child_resources(field.of)
        if child_resources:
            schema = {
                "oneOf": [
                    self._schema_def(child_resource)
                    for child_resource in child_resources
                ]
            }
        else:
            schema = self._schema_def(field.of)

        if isinstance(field, odin.DictAs):
            pass

        elif isinstance(field, odin.ListOf):
            schema = {"type": "array", "items": schema}

        elif isinstance(field, odin.DictOf):
            schema = {"type": "object", "additionalProperties": schema}

        return schema

    def _schema_def(self, resource: Type[ResourceBase]) -> Dict[str, str]:
        """Convert a resource to a JSON schema definition."""
        meta = getmeta(resource)
        ref = meta.resource_name
        if ref not in self.defs:
            self.defs[ref] = None  # Placeholder to prevent recursion
            self.defs[ref] = self._resource_to_schema(meta)
        return {"$ref": f"#/$defs/{ref}"}


def dumps(resource: Type[ResourceBase]) -> str:
    """Dump a JSON schema for the given resource."""
    schema = JSONSchema(resource).to_dict()
    return json.dumps(schema, indent=2)


def dump(resource: Type[ResourceBase], fp: TextIO):
    """Dump a JSON schema for the given resource."""
    schema = JSONSchema(resource).to_dict()
    json.dump(schema, fp, indent=2)
