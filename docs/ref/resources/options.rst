#####################
Resource Meta options
#####################

Meta options are flags that can be applied to a resource to affect it's behaviour or
how it is dealt with via Odin tools.

Give your resource metadata by using an inner ``class Meta``, eg::

    class Book(odin.Resource):
        class Meta:
            name_space = "library"
            verbose_name_plural = "Books"

        title = odin.StringField()

Resource metadata is “anything that’s not a field”, module_name and human-readable
plural names (verbose_name and verbose_name_plural). None are required, and adding class
Meta to a resource is completely optional.

Meta Options
============

``name``
    Override the name of a resource. This is the codecs when serialising/de-serialising
    as a name to represent the resource. The default name is the name of the class used
    to define the resource.

``name_space``
    The name space is an optional string value that is used to group a set of common
    resources. Typically a namespace should be in the form of dot-atoms eg:
    *university.library* or *org.poweredbypenguins*. The default is no namespace.

``verbose_name``
    A long version of the name for used when displaying a resource or in generated
    documentation. The default *verbose_name* is a *name* attribute that has been
    converted to lower case and spaces put before each upper case character
    eg: ``LibraryBook`` -> "*library book*"

``verbose_name_plural``
    A pluralised version of the *verbose_name*. The default is to use the verbose name
    and append an 's' character. In the case of many words this does not work correctly
    so this attribute allows for the default behaviour to be overridden.

``abstract``
    Marks the current resource as an **abstract** resource. See the section
    :ref:`resources-abstract` for more detail of the abstract attribute. The default
    value for *abstract* is :const:`False`.

``doc_group``
    A grouping for documentation purposes. This is purely optional but is useful for
    grouping common elements together. The default value for *doc_group* is
    :class:`None`.

``type_field``
    The field used to identify the object type during serialisation/de-serialisation.
    This defaults to the ``$`` character.

``key_field_name``
    Used by external libraries like ``baldr`` for identifying what field is used as
    the key field to uniquely identify a resource instance (a good example would be
    an ID field).

``key_field_names``
    Similar to the ``key_field_name`` but for defining multi-part keys.

``field_sorting``
    Used to customise how fields are sorted (primarily affects the order fields will
    be exported during serialisation) during inheritance. The default behaviour is
    to sort fields in the child resource before appending the fields from the parent
    resource(s).

    Settings this option to ``True`` will cause field sorting to happen after all of
    the fields have been attached using the default sort method. The default method
    sorts the fields by the order they are defined.

    Supplying a callable allows for customisation of the field sorting eg sort by
    name::

        def sort_by_name(fields):
            return sorted(fields, key=lambda f: f.name)

        class MyResource(Resource):
            class Meta:
                field_sorting = sort_by_name

