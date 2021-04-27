``{% if field.optional %}[{% endif %}{{ field.name }}{% if field.optional %}]{% endif %}``
  **{{ field.verbose_name|title }}**{% if field.optional %} *Optional*{% endif %}{% if field.help_text %} - {{ field.help_text }}{% endif %}{% if field.choices %}

  Options:
{% for choice in field.choices %}
  * {{ choice }}
{% endfor %}
{% endif %}
