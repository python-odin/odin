"""Rich Theme definition."""
from typing import Dict

from rich import get_console
from rich.style import Style
from rich.theme import Theme

ODIN_STYLES: Dict[str, Style] = {
    "odin.resource.name": Style(color="bright_cyan"),
    "odin.resource.error": Style(color="red", underline=True),
    "odin.field.name": Style(color="bright_blue"),
    "odin.field.error": Style(color="red", italic=True),
    "odin.field.type": Style(color="magenta"),
    "odin.field.doc": Style(),
}

odin_theme = Theme(ODIN_STYLES, inherit=False)


def add_odin_theme():
    """Add odin to builtin theme."""
    get_console().push_theme(odin_theme)
