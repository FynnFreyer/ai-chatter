{% extends "!template.rst" %}

{% block methods %}
{{ super() }}
{% for name, signature, summary, real_mod_name, mod_name in methods %}
{{ real_mod_name }}.{{ name }}{{ signature }}
    {{ summary }}
{% endfor %}
{% endblock %}