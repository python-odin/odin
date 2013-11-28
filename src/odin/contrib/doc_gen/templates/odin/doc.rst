{% extends "jsrn/base.rst" %}

{% block body %}
{% for resource in resources %}
{% include "odin/resource.rst" %}{% endfor %}
{% endblock %}