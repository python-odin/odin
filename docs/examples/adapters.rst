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


Adding functions to a resource
==============================

I have a resource that defines a set of results from a simulation. I want to be able to render the results of this
simulation into several different formats (eg an HTML table, a text file, a chart).

One approach would be to decorate the resource with different methods for each type of output eg *to_html*, *to_text*
etc but this has a number of drawbacks:

+ The resource has a lot of extra methods any new formats will require even of these methods
+ The size of the code is greatly increased
+ Rendering code is now mixed in with your data structure definition
+ In a larger team there is more chances of multiple people working on the same file making merges more complex
+ If I define another resource for a different set of results, sharing common code is more complex.

Again the :py:class:`odin.adapters.ResourceAdapter` class simplifies this.

By defining a rendering adapter for each of your different targets, the rendering code for each of these targets is now
encapsulated::

    class HtmlRenderingAdapter(odin.ResourceAdapter):
        def render(self):
            ...


    class TextRenderingAdapter(odin.ResourceAdapter):
        def render(self):
            ...


Each of these adapters can exist in their own file, also as they both include the same *render* interface they can be
passed to code that understands that adapter and finally because they are both classes they could both inherit off a
common base class that provides common code that is related to each rendering operation.
