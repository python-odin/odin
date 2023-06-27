"""JSON schema support for Odin."""
import json
from typing import Any, Dict, Final, List, Sequence, TextIO, Tuple, Type, Union

import odin
import odin.validators
from odin.registration import get_child_resources
from odin.resources import ResourceBase, ResourceOptions
from odin.utils import getmeta

SCHEMA_DIALECT: Final[str] = "https://json-schema.org/draft/2020-12/schema"
FIELD_SCHEMAS = {
    odin.StringField: ("string", {}),
    odin.BooleanField: ("boolean", {}),
    odin.IntegerField: ("integer", {}),
    odin.FloatField: ("number", {}),
    odin.ListField: ("array", {}),
    odin.DictField: ("object", {}),
    odin.DateField: ("string", {"format": "date"}),
    odin.TimeField: ("string", {"format": "time"}),
    odin.DateTimeField: ("string", {"format": "date-time"}),
    odin.EmailField: ("string", {"format": "email"}),
    odin.IPv4Field: ("string", {"format": "ipv4"}),
    odin.IPv6Field: ("string", {"format": "ipv6"}),
    odin.IPv46Field: ("string", {"format": ["ipv4", "ipv6"]}),
    odin.PathField: ("string", {}),
    odin.RegexField: ("string", {"format": "regex"}),
    odin.UrlField: ("string", {"format": "uri"}),
    odin.UUIDField: ("string", {"format": "uuid"}),
}
VALIDATOR_SCHEMAS = {
    odin.validators.MaxValueValidator: {},
    odin.validators.MinValueValidator: {},
    odin.validators.LengthValidator: {},
    odin.validators.MaxLengthValidator: {},
    odin.validators.MinLengthValidator: {},
}
JSON_SCHEMA_METHOD: Final[str] = "as_json_schema"


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
            schema = self._composite_field_to_schema(field)

        else:
            type_def, extra_schema = self._field_type(field)
            schema = {"type": type_def}
            schema.update(extra_schema)

        if field.doc_text:
            schema["description"] = field.doc_text
        if field.choices:
            schema.setdefault("enum", field.choice_values)

        return schema

    def _field_type(
        self, field: odin.Field
    ) -> Tuple[Union[str, List[str]], Dict[str, Any]]:
        """Get the type of a field."""

        field_type = type(field)

        if method := getattr(field, JSON_SCHEMA_METHOD, None):
            type_name, schema = method()

        elif field_type in FIELD_SCHEMAS:
            type_name, schema = FIELD_SCHEMAS[field_type]

        elif isinstance(field, odin.EnumField):
            type_name = "string"
            schema = {"enum": tuple(str(item.value) for item in field.enum_type)}

        elif isinstance(field, odin.TypedListField):
            type_name = "array"
            schema = {"items": self._field_to_schema(field.field)}

        elif isinstance(field, odin.TypedDictField):
            type_name = "object"
            schema = {"additionalProperties": self._field_to_schema(field.value_field)}

        else:
            for field_type, field_info in FIELD_SCHEMAS.items():
                if isinstance(field, field_type):
                    type_name, schema = field_info
                    break

            else:
                raise ValueError(f"Unknown field type: {field_type}")

        return ([type_name, "null"] if field.null else type_name), schema

    def _composite_field_to_schema(self, field: odin.CompositeField) -> Dict[str, Any]:
        """Convert a composite field to a JSON schema."""

        # Handle abstract resources
        child_resources = get_child_resources(field.of)
        if child_resources:
            if len(child_resources) == 1:
                schema = self._schema_def(child_resources[0])
            else:
                schema = {
                    "oneOf": [
                        self._schema_def(child_resource)
                        for child_resource in child_resources
                    ]
                }
        else:
            schema = self._schema_def(field.of)

        if isinstance(field, odin.ListOf):
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
