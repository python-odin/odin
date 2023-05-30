"""
XML Codec (output only)

Output a resource structure as XML

XML has a unique attribute in the form of the text. This is plain text that can
be placed within a pair of tags.

To support this the XML codec includes a TextField, any TextField found on a
resource will be exported (if multiple are defined they will all be exported
into the one text block).

The TextField is for all intents and purposes just a StringField, other codecs
will export any value as a String.

"""
import datetime
from io import StringIO
from typing import TextIO
from xml.sax import saxutils

from odin import fields, serializers
from odin.fields import StringField, composite
from odin.utils import attribute_field_iter_items, element_field_iter_items, getmeta

XML_TYPES = {
    datetime.date: serializers.date_iso_format,
    datetime.time: serializers.time_iso_format,
    datetime.datetime: serializers.datetime_iso_format,
}

CONTENT_TYPE = "application/xml"


class TextField(StringField):
    """
    Special String field for representing XML text blocks.
    """


def _serialize_to_string(value):
    if value.__class__ in XML_TYPES:
        return XML_TYPES[value.__class__](value)
    else:
        return str(value)


def dump(
    fp: TextIO,
    resource,  # type: Resource
    line_ending: str = "",
):
    """
    Dump a resource to a file like object.
    :param fp: File pointer or file like object.
    :param resource: Resource to dump
    :param line_ending: End of line character to apply
    """
    meta = getmeta(resource)

    # Write container and any attributes
    attributes = "".join(
        f" {f.name}={saxutils.quoteattr(_serialize_to_string(v))}"  # Encode attributes
        for f, v in attribute_field_iter_items(resource)
    )
    fp.write(f"<{meta.name}{attributes}>{line_ending}")

    # Write any element fields
    for field, value in element_field_iter_items(resource):
        if isinstance(field, composite.ListOf):
            if field.use_container:
                fp.write(f"<{field.name}>{line_ending}")
            for v in value:
                dump(fp, v, line_ending)
            if field.use_container:
                fp.write(f"</{field.name}>{line_ending}")

        elif isinstance(field, composite.DictAs):
            if value is not None:
                dump(fp, value, line_ending)

        elif isinstance(field, fields.ArrayField):
            for v in value:
                fp.write(
                    f"<{field.name}>{_serialize_to_string(v)}</{field.name}>{line_ending}"
                )

        elif isinstance(field, TextField):
            if value is not None:
                fp.write(f"{saxutils.escape(_serialize_to_string(value))}{line_ending}")

        else:
            fp.write(
                f"<{field.name}>{saxutils.escape(_serialize_to_string(value))}</{field.name}>{line_ending}"
            )

    fp.write(f"</{meta.name}>{line_ending}")


def dumps(resource, **kwargs):
    """
    Dump a resource to a string.

    :param resource: Resource to dump
    """
    f = StringIO()
    dump(f, resource, **kwargs)
    return f.getvalue()
