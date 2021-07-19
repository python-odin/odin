################
Sphinx Extension
################

Odin provides a Sphinx extension for documenting resources. It behaves similarly to the builtin Autodoc tools.

Setup
=====

Add the Odin extension into your Sphinx `conf.py`::

    extensions = [
        ...
        'odin.contrib.sphinx',
        ...
    ]


Usage
=====

Extension to ``sphinx.ext.autodoc`` to support documenting Odin resources.

This extension supports output in two forms, class doc form (for documenting the python objects) and API form for
documenting information about fields for use in an API document.

Usage::

    .. autoodin-resource:: namespace.path.to.your.Resource
        :include_virtual:
        :hide_choices:

To select API form use the *include_virtual* option.


Options
-------

The following options are provided by the documenter:

- ``include_virtual`` virtual fields should be included in docs

- ``include_validators`` validators should be listed for fields

- ``hide_choices`` don't include the list of valid choices for fields
