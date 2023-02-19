#########
Traversal
#########

Traversal package provides tools for iterating and navigating a resource tree.

.. automodule:: odin.traversal


TraversalPath
=============

A method of defining a location within a data structure, which can then be applied to
the datastructure to extract the value.

A ``TraversalPath`` can be expressed as a string using ``.`` as a separator::

    field1.field2

Both lists and dicts can be included using ``[]`` and ``{}`` syntax::

    field[1].field2

or::

    field{key=value}.field2


ResourceTraversalIterator
=========================

Iterator for traversing (walking) a resource structure, including traversing composite fields to fully navigate a
resource tree.

This class has hooks that can be used by subclasses to customise the behaviour of the class:

 - *on_enter* - Called after entering a new resource.
 - *on_exit* - Called after exiting a resource.

.. autoclass:: odin.traversal.ResourceTraversalIterator
   :members:
