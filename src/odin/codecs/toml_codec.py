from collections.abc import Sequence

from odin import ResourceAdapter, resources
from odin.exceptions import CodecDecodeError
from odin.resources import ResourceBase

try:
    import toml
except ImportError:  # pragma: no cover
    raise ImportError(  # pragma: no cover
        "odin.codecs.toml_codec requires the 'toml' package."
    ) from None


TOML_TYPES = {}
CONTENT_TYPE = "application/toml"


def load(fp, resource=None, full_clean=True, default_to_not_supplied=False):
    """
    Load a resource from a TOML encoded file.

    If a ``resource`` value is supplied it is used as the base resource for the
    supplied YAML. If one is not supplied, a resource type field ``$`` is used to
    obtain the type represented by the dictionary. A ``ValidationError`` will be
    raised if either of these values are supplied and not compatible. It is valid for a
    type to be supplied in the file to be a child object from within the inheritance
    tree.

    :param fp: a file pointer to read TOML data format.
    :param resource: A resource type, resource name or list of resources and names to
        use as the base for creating a resource. If a list is supplied the first item
        will be used if a resource type is not supplied.
    :param full_clean: Do a full clean of the object as part of the loading process.
    :param default_to_not_supplied: Used for loading partial resources. Any fields not
        supplied are replaced with NOT_SUPPLIED.
    :returns: A resource object or object graph of resources loaded from file.

    """

    try:
        data = toml.load(fp)
    except toml.TomlDecodeError as ex:
        raise CodecDecodeError(str(ex)) from ex

    return resources.build_object_graph(
        data,
        resource,
        full_clean,
        False,
        default_to_not_supplied,
    )


def loads(s, resource=None, full_clean=True, default_to_not_supplied=False):
    """Load a resource from a TOML encoded string.

    If a ``resource`` value is supplied it is used as the base resource for the
    supplied YAML. If one is not supplied, a resource type field ``$`` is used to
    obtain the type represented by the dictionary. A ``ValidationError`` will be raised
    if either of these values are supplied and not compatible. It is valid for a type
    to be supplied in the file to be a child object from within the inheritance tree.

    :param s: a string containing TOML.
    :param resource: A resource type, resource name or list of resources and names to
        use as the base for creating a resource. If a list is supplied the first item
        will be used if a resource type is not supplied.
    :param full_clean: Do a full clean of the object as part of the loading process.
    :param default_to_not_supplied: Used for loading partial resources. Any fields not
        supplied are replaced with NOT_SUPPLIED.
    :returns: A resource object or object graph of resources loaded from file.

    """

    try:
        data = toml.loads(s)
    except toml.TomlDecodeError as ex:
        raise CodecDecodeError(str(ex)) from ex

    return resources.build_object_graph(
        data,
        resource,
        full_clean,
        False,
        default_to_not_supplied,
    )


class OdinEncoder(toml.TomlEncoder):
    """Encode that handles Odin types."""

    def __init__(
        self,
        include_virtual_fields: bool = True,
        include_type_field: bool = True,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.include_virtual_fields = include_virtual_fields
        self.include_type_field = include_type_field

    def resource_to_dict(self, v):
        return v.to_dict(self.include_virtual_fields, self.include_type_field)

    def dump_value(self, v):
        if isinstance(v, ResourceBase | ResourceAdapter):
            resource_dict = self.resource_to_dict(v)
            return self.dump_inline_table(resource_dict)

        if type(v) in TOML_TYPES:
            v = TOML_TYPES[type(v)](v)
        return super().dump_value(v)


RT = (
    ResourceBase
    | ResourceAdapter
    | Sequence[ResourceBase]
    | Sequence[ResourceAdapter]
    | dict,
)


def dump(
    resource: RT,
    fp,
    encoder: type[OdinEncoder] | None = None,
    include_virtual_fields: bool = True,
    **kwargs,
):
    """Dump to a TOML encoded file.

    :param resource: The root resource to dump to a JSON encoded file.
    :param fp: The file pointer that represents the output file.
    :param encoder: Encoder to use serializing to a string; default is the
        :py:class:`OdinEncoder`.
    :param include_virtual_fields: Include virtual fields in the output
    :param kwargs: Additional keyword arguments for the encoder.
    """
    encoder = (encoder or OdinEncoder)(include_virtual_fields, **kwargs)

    if isinstance(resource, ResourceBase | ResourceAdapter):
        resource = encoder.resource_to_dict(resource)

    toml.dump(resource, fp, encoder)


def dumps(
    resource: RT,
    encoder: type[OdinEncoder] | None = None,
    include_virtual_fields: bool = True,
    **kwargs,
) -> str:
    """Dump to a TOML encoded file.

    :param resource: The root resource to dump to a JSON encoded file.
    :param encoder: Encoder to use serializing to a string; default is the
        :py:class:`OdinEncoder`.
    :param include_virtual_fields: Include virtual fields in the output
    :param kwargs: Additional keyword arguments for the encoder.
    :returns: TOML encoded string.
    """
    encoder = (encoder or OdinEncoder)(include_virtual_fields, **kwargs)

    if isinstance(resource, ResourceBase | ResourceAdapter):
        resource = encoder.resource_to_dict(resource)

    return toml.dumps(resource, encoder)
