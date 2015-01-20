# -*- coding: utf-8 -*-
import six


def _split_atom(atom):
    field, _, key = atom.rstrip(']').partition('[')
    return key or None, field


class TraversalPath(object):
    """
    A path through a resource structure.
    """
    @classmethod
    def parse(cls, path):
        if isinstance(path, six.string_types):
            return cls(*[_split_atom(a) for a in path.split('.')])

    def __init__(self, *path):
        self._path = path

    def __repr__(self):
        return "<TraversalPath: %s>" % self

    def __str__(self):
        return '.'.join("%s" % f if k is None else "%s[%s]" % (f, k) for k, f in self._path)

    def __hash__(self):
        return hash(self._path)

    def __eq__(self, other):
        if isinstance(other, TraversalPath):
            return hash(self) == hash(other)
        return False

    def __add__(self, other):
        if isinstance(other, TraversalPath):
            return TraversalPath(*(self._path + other._path))

        # Assume appending a field
        if isinstance(other, six.string_types):
            return TraversalPath(*(self._path + tuple([(None, other)])))

        raise TypeError("Cannot add '%s' to a path." % other)

    def __iter__(self):
        return iter(self._path)

    def get_value(self, root_resource):
        """
        Get a value from a resource structure.
        """
        value = root_resource
        for key, attr in self:
            field = value._meta.field_map[attr]
            value = field.value_from_object(value)
            if key is not None:
                key = field.key_to_python(key)
                value = value[key]
        return value


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
        self._path = [(None, None)]
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
                    self._path.append((None, field.name))
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
                # If we have a key (ie DictOf, ListOf composite fields) update the path key field.
                if key is not None:
                    _, field = self._path[-1]
                    self._path[-1] = (key, field)

                # Get list of any composite fields for this resource (this is a cached field).
                self._field_iters.append(list(next_resource._meta.composite_fields))

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
