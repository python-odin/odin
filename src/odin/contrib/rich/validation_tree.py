"""Integration with Rich for nicer CLI's!"""
from typing import Iterable, Union

from rich.tree import Tree

from odin.exceptions import NON_FIELD_ERRORS, ValidationError


def _all_str(iterable: Iterable) -> bool:
    """Does the supplied iterable only contain strings."""
    return all(isinstance(item, str) for item in iterable)


def _validation_error_to_tree(error_messages: Union[list, dict], tree: Tree):
    """Internal recursive method."""

    if isinstance(error_messages, dict):
        for name, value in error_messages.items():
            node = tree.add(
                "[odin.resource.name]+"
                if name == NON_FIELD_ERRORS
                else f"[odin.field.name]{name}"
            )

            _validation_error_to_tree(value, node)

    elif isinstance(error_messages, list):
        if _all_str(error_messages):
            for message in error_messages:
                tree.add(f"[odin.field.error]{message}", guide_style="bold")

        else:
            for idx, value in enumerate(error_messages):
                node = tree.add(str(idx))
                _validation_error_to_tree(value, node)

    else:
        # Shouldn't technically be possible with a valid error messages structure.
        tree.add(f":warning: {error_messages}")


def validation_error_tree(error: ValidationError, *, tree: Tree = None) -> Tree:
    """Map a validation error into a tree.

    .. codeblock:: python

        error_tree = validation_error_to_tree(error)
        print(tree)

    """
    tree = tree or Tree(
        "[red bold]Validation Errors",
    )
    _validation_error_to_tree(error.error_messages, tree)
    return tree
