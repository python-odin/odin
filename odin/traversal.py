# -*- coding: utf-8 -*-
import six
from odin.utils import getmeta

from .exceptions import NoMatchError, MultipleMatchesError, InvalidPathError


class NotSupplied(object):
    pass


def _split_atom(atom):
    if '[' in atom:
        field, _, idx = atom.rstrip(']').partition('[')
        return idx, NotSupplied, field
    elif '{' in atom:
        field, _, kv = atom.rstrip('}').partition('{')
        key, _, value = kv.partition('=')
        return value, key, field
    else:
        return NotSupplied, NotSupplied, atom


class TraversalPath(object):
    """
    A path through a resource structure.
    """
    @classmethod
    def parse(cls, path):
        if isinstance(path, TraversalPath):
            return path
        if isinstance(path, six.string_types):
            return cls(*[_split_atom(a) for a in path.split('.')])

    def __init__(self, *path):
        self._path = path

    def __repr__(self):
        return "<TraversalPath: {0}>".format(self)

    def __str__(self):
        atoms = []
        for value, key, field in self._path:
            if value is NotSupplied:
                atoms.append(field)
            elif key is NotSupplied:
                atoms.append("{0}[{1}]".format(field, value))
            else:
                atoms.append("{0}{{{1}={2}}}".format(field, key, value))
        return '.'.join(atoms)

    def __hash__(self):
        return hash(self._path)

    def __eq__(self, other):
        if isinstance(other, TraversalPath):
            return hash(self) == hash(other)
        return NotImplemented

    def __add__(self, other):
        if isinstance(other, TraversalPath):
            return TraversalPath(*(self._path + other._path))

        # Assume appending a field
        if isinstance(other, six.string_types):
            return TraversalPath(*(self._path + tuple([(NotSupplied, NotSupplied, other)])))

        raise TypeError("Cannot add '%s' to a path." % other)

    def __iter__(self):
        return iter(self._path)

    def get_value(self, root_resource):
        """
        Get a value from a resource structure.
        """
        result = root_resource
        for value, key, attr in self:
            meta = getmeta(result)
            try:
                field = meta.field_map[attr]
            except KeyError:
                raise InvalidPathError(self, "Unknown field `{0}`".format(attr))

            result = field.value_from_object(result)
            if value is NotSupplied:
                # Nothing is required
                continue
            elif key is NotSupplied:
                # Index or key into element
                value = field.key_to_python(value)
                try:
                    result = result[value]
                except (KeyError, IndexError):
                    raise NoMatchError(self, "Could not find index `{0}` in {1}.".format(value, field))
            else:
                # Filter elements
                if isinstance(result, dict):
                    result = result.values()
                results = tuple(r for r in result if getattr(r, key) == value)
                if len(results) == 0:
                    raise NoMatchError(
                        self, "Filter matched no values; `{0}` == `{1}` in {2}.".format(key, value, field))
                elif len(results) > 1:
                    raise MultipleMatchesError(
                        self, "Filter matched multiple values; `{0}` == `{1}`.".format(key, value))
                else:
                    result = results[0]
        return result


class ResourceTraversalIterator(object):
    """
    Iterator for traversing (walking) a resource structure, including traversing composite fields to fully navigate a
    resource tree.

    This class has hooks that can be used by subclasses to customise the behaviour of the class:

     - *on_enter* - Called after entering a new resource.
     - *on_exit* - Called after exiting a resource.

    """
    def __init__(self, resource):
        if isinstance(resource, (list, tuple)):
            # Stack of resource iterators (starts initially with entries from the list)
            self._resource_iters = [iter([(i, r) for i, r in enumerate(resource)])]
        else:
            # Stack of resource iterators (starts initially with single entry of the root resource)
            self._resource_iters = [iter([(None, resource)])]
        # Stack of composite fields, found on each resource, each composite field is interrogated for resources.
        self._field_iters = []
        # The "path" to the current resource.
        self._path = [(NotSupplied, NotSupplied, NotSupplied)]
        self._resource_stack = [None]

    def __iter__(self):
        return self

    def __next__(self):
        if self._resource_iters:
            if self._field_iters:
                # Check if the last entry in the field stack has any unprocessed fields.
                if self._field_iters[-1]:
                    # Select the very last field in the field stack.
                    field = self._field_iters[-1][0]
                    # Request a list of resources along with keys from the composite field.
                    self._resource_iters.append(field.item_iter_from_object(self.current_resource))
                    # Update the path
                    self._path.append((NotSupplied, NotSupplied, field.name))
                    self._resource_stack.append(None)
                    # Remove the field from the list (and remove this field entry if it has been emptied)
                    self._field_iters[-1].pop(0)
                else:
                    self._field_iters.pop()

            if self.current_resource:
                if hasattr(self, 'on_exit'):
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
                    _, name, field = self._path[-1]
                    if next_meta.key_field:
                        key = next_meta.key_field.value_from_object(next_resource)
                        name = next_meta.key_field.name
                    self._path[-1] = (key, name, field)

                # Get list of any composite fields for this resource (this is a cached field).
                self._field_iters.append(list(next_meta.composite_fields))

                # self.current_resource = next_resource
                self._resource_stack[-1] = next_resource

                if hasattr(self, 'on_enter'):
                    self.on_enter()
                return next_resource
        else:
            raise StopIteration()

    # Python 2.x compatibility
    next = __next__

    @property
    def path(self):
        """
        Path to the current resource node in the tree structure.

        This path can be used to later traverse the tree structure to find get to the specified resource.
        """
        # The path is offset by one as the path includes the root to simplify next method.
        return TraversalPath(*self._path[1:])

    @property
    def depth(self):
        """
        Depth of the current resource in the tree structure.
        """
        return len(self._path) - 1

    @property
    def current_resource(self):
        if self._resource_stack:
            return self._resource_stack[-1]
