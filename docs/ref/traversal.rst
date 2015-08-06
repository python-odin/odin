#########
Traversal
#########

Traversal package provides tools for iterating and navigating a resource tree.

.. automodule:: odin.traversal


TraversalPath
=============

*Todo*: In progress...


ResourceTraversalIterator
=========================

Iterator for traversing (walking) a resource structure, including traversing composite fields to fully navigate a
resource tree.

This class has hooks that can be used by subclasses to customise the behaviour of the class:

 - *on_enter* - Called after entering a new resource.
 - *on_exit* - Called after exiting a resource.
