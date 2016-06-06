################
Adapter Examples
################

Filtering out fields
====================

There are many times where certain fields need to be filtered from a resource before the resource is serialised (either
to file or into an HTTP response). This could be to remove any sensitive information, or internal debug fields that
should not be returned to an API. The :py:class:`odin.adapters.ResourceAdapter` class makes this trivial.

Which fields should be filtered can be defined in one of two ways::

    # At instantiation to allowing for dynamic filtering
    my_filtered_resource = odin.ResourceAdapter(my_resource, exclude=('password',))

    # Of predefined if this adapter will be used multiple times (not an adapter is not tied to any particular resource
    # type so a single adapter could be used to filter the password field from any resource)
    class PasswordFilter(odin.ResourceAdapter):
        exclude = ['password',]

    my_filtered_resource = PasswordFilter(my_resource)


.. note: A predefined adapter can still accept additional exclude fields at instantiation, the additional fields will
    simply be appended to the predefined exclude list.


Added additional functionality to a resource
============================================

I have a resource that define a set of simulation results. I want to be able to render the results of this
simulation into several different formats eg an HTML table, a text file, a chart.

One approach would be to add to a method to the resource for each of the formats I wich to render like *to_html* or *to_text*, however this has a number of drawbacks:

+ The resource is not more complex with an additional method for each of the target formats
+ Rendering code is now mixed in with your data structure definition
+ In a larger team there is more chances of multiple people working on the same file making merges more complex
+ If I define another resource for a different set of results, sharing common code is harder
+ The resource has a different interface for each method

The :py:class:`odin.adapters.ResourceAdapter` class simplifies this.

By defining a rendering adapter for each of the different targets, the rendering code for each of these targets is encapsulated in a single class::

    class HtmlRenderingAdapter(odin.ResourceAdapter):
        def render(self):
            ...


    class TextRenderingAdapter(odin.ResourceAdapter):
        def render(self):
            ...


The benefits of this approach:

+ All features required for each render adapter are encapsulated
+ Each of these adapters can exist in their own file
+ Both adapters include the same *render* interface they can be passed to code that understands that interface
+ Both classes can both inherit off a common base class that provides common code that is related to each rendering operation.
