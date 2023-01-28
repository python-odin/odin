#######################
Integration with Django
#######################


Mapping Django models to resources
==================================

To utilise a Django database model in a :doc:`/ref/mapping/index` a
``FieldResolver`` is required to identify fields available on the model.

The following is an example of a resolver for Django models.

.. code-block:: python

    from odin import registration
    from odin.utils import getmeta
    from odin.mapping import FieldResolverBase


    class ModelFieldResolver(FieldResolverBase):
        """
        Field resolver for Django Models
        """

        def get_field_dict(self):
            meta = getmeta(self.obj)
            return {f.attname: f for f in meta.fields}


    registration.register_field_resolver(ModelFieldResolver, models.Model)
