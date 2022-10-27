from odin.fields import Field


class AnyField(Field):
    """
    A field that can hold Any (typically that can be handled by the codec) value.

    This might seem counterintuitive however this feature can be used with a typed dict
    to allow for dynamic configuration parameters (although this is discouraged).

    The main use for this field is the Any type for Annotated resources
    """

    data_type_name = "Any"

    def to_python(self, value):
        # Do nothing any value is good
        return value
