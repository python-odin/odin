"""Traversal of a datastructure."""
import itertools
from typing import Any, Iterable, List, NamedTuple, Optional, Sequence, Union, cast

import odin
from odin.exceptions import InvalidPathError, MultipleMatchesError, NoMatchError
from odin.resources import ResourceBase
from odin.utils import getmeta


class _NotSupplied:
    """Placeholder"""

    __slots__ = ()


NotSupplied = _NotSupplied()
NotSuppliedString = Union[str, _NotSupplied]


class PathAtom(NamedTuple):
    """Atom within a traversal path."""

    @classmethod
    def split(cls, atom: str) -> "PathAtom":
        # Index/Key into attribute
        if "[" in atom:
            attr, _, key = atom.rstrip("]").partition("[")
            return cls(key, NotSupplied, attr)

        # Filter attributes
        if "{" in atom:
            attr, _, kv = atom.rstrip("}").partition("{")
            key, _, value = kv.partition("=")
            return cls(key, value, attr)

        # Basic attribute
        return cls(NotSupplied, NotSupplied, atom)

    @classmethod
    def create(
        cls,
        attr: str = "",
        key: NotSuppliedString = NotSupplied,
        value: NotSuppliedString = NotSupplied,
    ) -> "PathAtom":
        """Create a new PathAtom."""
        return cls(key, value, attr)

    key: NotSuppliedString
    value: NotSuppliedString
    attr: str

    def __repr__(self):
        return f"<PathAtom: {self}>"

    def __str__(self):
        key, value, attr = self

        if key is NotSupplied:
            return attr

        if value is NotSupplied:
            return f"{attr}[{key}]"

        return f"{attr}{{{key}={value}}}"

    @property
    def is_indexed(self) -> bool:
        """Indexes into a attribute."""
        key, value, _ = self
        return key is not NotSupplied and value is NotSupplied

    @property
    def is_filter(self) -> bool:
        """This is a filter atom."""
        _, value, _ = self
        return value is not NotSupplied

    def extract_element(self, resource: ResourceBase) -> Any:
        """Extract an element from a resource instance"""
        key, value, attr = self

        try:
            field = getmeta(resource).field_map[attr]
        except KeyError:
            raise InvalidPathError(self, f"Unknown field {attr!r}") from None
        element = field.value_from_object(resource)

        if key is NotSupplied:
            # No additional lookup required
            return element

        elif value is NotSupplied:
            # Index or key into element
            key = cast(odin.CompositeField, field).key_to_python(key)
            try:
                return element[key]
            except LookupError:
                raise NoMatchError(
                    self, f"Could not find index {key!r} in {field}."
                ) from None

        else:
            # Filter elements
            if isinstance(element, dict):
                element = element.values()

            values = tuple(r for r in element if getattr(r, key) == value)
            if len(values) == 0:
                raise NoMatchError(
                    self,
                    f"Filter matched no values; {key!r} == {value!r} in {field}.",
                )

            if len(values) > 1:
                raise MultipleMatchesError(
                    self,
                    f"Filter matched multiple values; {key!r} == {value!r}.",
                )

            return values[0]


class TraversalPath(tuple, Sequence[PathAtom]):
    """A path through a resource structure."""

    @classmethod
    def parse(cls, path: Union["TraversalPath", str]) -> Optional["TraversalPath"]:
        """Parse a traversal path string."""
        if isinstance(path, TraversalPath):
            return path
        if isinstance(path, str):
            return cls(PathAtom.split(a) for a in path.split(".")) if path else cls()

    __slots__ = ()

    def __repr__(self):
        return f"<TraversalPath: {self}>"

    def __str__(self) -> str:
        return ".".join(str(a) for a in self)

    def __add__(self, other: Union["TraversalPath", str, PathAtom]) -> "TraversalPath":
        """Join paths together."""
        if isinstance(other, TraversalPath):
            return TraversalPath(itertools.chain(self, other))

        if isinstance(other, str):
            other = PathAtom.split(other)

        if isinstance(other, PathAtom):
            return TraversalPath(itertools.chain(self, (other,)))

        raise TypeError(f"Cannot add '{other}' to a path.")

    @property
    def parent(self) -> Optional["TraversalPath"]:
        """Get parent item"""
        if len(self) > 1:
            return TraversalPath(self[:-1])

    def iter_resource(self, root_resource: ResourceBase):
        """Iterate over a resource document. Yielding each parent."""
        current = root_resource
        yield current

        for atom in self:
            current = atom.extract_element(current)
            yield current

    def get_value(self, root_resource: ResourceBase):
        """Get a value from a resource document."""
        return tuple(self.iter_resource(root_resource))[-1]


class ResourceTraversalIterator:
    """Iterator for traversing (walking) a resource structure, including traversing
    composite fields to fully navigate a resource tree.

    This class has hooks that can be used by subclasses to customise the behaviour of the class:

     - *on_enter* - Called after entering a new resource.
     - *on_exit* - Called after exiting a resource.

    """

    __slots__ = ("_resource_iters", "_field_iters", "_path", "_resource_stack")

    def __init__(self, resource: Union[ResourceBase, Sequence[ResourceBase]]):
        """Initialise instance with the initial resource or sequence of resources."""
        if isinstance(resource, (list, tuple)):
            # Stack of resource iterators (starts initially with entries from the list)
            self._resource_iters = [iter([(i, r) for i, r in enumerate(resource)])]
        else:
            # Stack of resource iterators (starts initially with single entry of the root resource)
            self._resource_iters = [iter([(None, resource)])]
        # Stack of composite fields, found on each resource, each composite field is interrogated for resources.
        self._field_iters = []
        # The "path" to the current resource.
        self._path: List[PathAtom] = [PathAtom.create()]
        self._resource_stack = [None]

    def __iter__(self) -> Iterable[ResourceBase]:
        """Obtain an iterable instance."""
        return self

    def __next__(self) -> ResourceBase:
        """Get next resource instance."""
        if not self._resource_iters:
            raise StopIteration()

        if self._field_iters:
            # Check if the last entry in the field stack has any unprocessed fields.
            if self._field_iters[-1]:
                # Select the very last field in the field stack.
                field = self._field_iters[-1][0]
                # Request a list of resources along with keys from the composite field.
                self._resource_iters.append(
                    field.item_iter_from_object(self.current_resource)
                )
                # Update the path
                self._path.append(PathAtom.create(field.attname))
                self._resource_stack.append(None)
                # Remove the field from the list (and remove this field entry if it has been emptied)
                self._field_iters[-1].pop(0)
            else:
                self._field_iters.pop()

        if self.current_resource and hasattr(self, "on_exit"):
            self.on_exit()

        try:
            key, next_resource = next(self._resource_iters[-1])
        except StopIteration:
            # End of the current list of resources pop this list off and get the next list.
            self._path.pop()
            self._resource_iters.pop()
            self._resource_stack.pop()
            return next(self)

        else:
            next_meta = getmeta(next_resource)
            # If we have a key (ie DictOf, ListOf composite fields) update the path key field.
            if key is not None:
                _, value, field = self._path[-1]
                if next_meta.key_field:
                    value = next_meta.key_field.value_from_object(next_resource)
                    key = next_meta.key_field.attname
                self._path[-1] = PathAtom(key, value, field)

            # Get list of any composite fields for this resource (this is a cached field).
            self._field_iters.append(list(next_meta.composite_fields))

            # self.current_resource = next_resource
            self._resource_stack[-1] = next_resource

            if hasattr(self, "on_enter"):
                self.on_enter()
            return next_resource

    @property
    def path(self) -> TraversalPath:
        """Path to the current resource node in the tree structure.

        This path can be used to later traverse the tree structure to find get to the specified resource.
        """
        # The path is offset by one as the path includes the root to simplify next method.
        return TraversalPath(self._path[1:])

    @property
    def depth(self) -> int:
        """Depth of the current resource in the tree structure."""
        return len(self._path) - 1

    @property
    def current_resource(self) -> Optional[ResourceBase]:
        """The current resource being traversed."""
        if self._resource_stack:
            return self._resource_stack[-1]
