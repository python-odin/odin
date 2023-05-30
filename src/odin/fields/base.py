from typing import Callable, Optional


class BaseField:
    """Base all field inherit from."""

    # These track each time an instance is created. Used to retain order.
    creation_counter = 0

    def __init__(
        self,
        verbose_name: str = None,
        verbose_name_plural: str = None,
        name: str = None,
        doc_text: str = "",
    ):
        self.verbose_name, self.verbose_name_plural = verbose_name, verbose_name_plural
        self.name = name
        self.doc_text = doc_text

        # Fetch and increment the creation counter
        self.creation_counter = BaseField.creation_counter
        BaseField.creation_counter += 1

        self.attname: Optional[str] = None

    def __hash__(self):
        return self.creation_counter

    def __repr__(self):
        """Displays the module, class and name of the field."""
        path = f"{self.__class__.__module__}.{self.__class__.__name__}"
        name = getattr(self, "name", None)
        if name is not None:
            return f"<{path}: {name}>"
        return f"<{path}>"

    def set_attributes_from_name(
        self, attname: str, name_formatter: Optional[Callable[[str], str]] = None
    ):
        """Pre-populate names and accepts an optional name formatter method."""
        if not self.name:
            self.name = name_formatter(attname) if name_formatter else attname
        self.attname = attname
        if self.verbose_name is None and self.name:
            self.verbose_name = self.name.replace("_", " ")
        if self.verbose_name_plural is None and self.verbose_name:
            self.verbose_name_plural = f"{self.verbose_name}s"

    def prepare(self, value):
        """Prepare a value for serialisation."""
        return value

    def as_string(self, value) -> Optional[str]:
        """Generate a string representation of a field."""
        if value is not None:
            return str(value)

    def value_from_object(self, obj):
        """Returns the value of this field in the given resource instance."""
        return getattr(obj, self.attname)
