####
Rich
####

Better CLI's with Rich!

.. note::

    This contrib module depends on the `Rich <https://rich.readthedocs.io/en/latest/introduction.html>`_ library::

        pip install rich



Render Validation Errors
========================

Generate a tree or extend an existing one from a ``ValidationError`` exception.

.. code-block:: python

    from rich import print
    from odin.contrib.rich.validation_tree import validation_error_tree

    try:
        ...
    except ValidationError as ex:
        tree = validation_error_tree(ex)
        print(tree)

.. note::
    A tree instance can be provided as the second argument to allow for customisations
    to the tree root label and styles.
