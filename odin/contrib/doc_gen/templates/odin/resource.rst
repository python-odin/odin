{{ resource.verbose_name|title }}
{{ '=' * resource.verbose_name|length }}
{% if resource.description %}
{{ resource.description }}{% endif %}

{% for field in resource.fields %}{% include "odin/field.rst" %}
{% endfor %}
