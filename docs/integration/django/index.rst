#######################
Integration with Django
#######################

Integration with `Django <https://www.djangoproject.com>`_ is via `baldr <https://github.com/python-odin/baldr>`_.

Baldr includes:

* ResourceField for saving a resource to a Django model.
* Field resolver for Django models, this allows you to map between Django models and Odin resources.
* RESTful API implementation using Odin resources.


ResourceField
=============

This is a field that handles serialisation/deserialisation of Odin resources from a database. Data is serialised as
JSON. It is basically a Django :class:`django.db.models.fields.TextField` with the additional required option
*resource*.

Example::

    class MyModel(models.Model):
        my_resource = ResourceField(MyResource)



Field resolver
==============

By including baldr as an application in Django the field resolver is automatically registered. From there you can write
mappings between Django models and Odin resources. Set either the to_resource or from_resource fields to be Django
models and that's it.


RESTful API
===========

One of the powerful features of Odin is validation of data that is loaded. This makes Odin perfect for handling RESTful
API's.

:todo: Expand on capabilities.