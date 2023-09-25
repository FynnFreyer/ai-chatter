{{ name | escape | underline }}

.. .. note::
    | {{ name }}
    | {{ module }}
    | {{ fullname }}

.. currentmodule:: {{ module }}

.. autoclass:: {{ fullname }}
   :members:
   :show-inheritance:
   :special-members: __add__, __mul__, __lt__, __le__

   {% block methods -%}
   {%- if methods | reject("in", inherited_members) | first -%}
   .. rubric:: {{ _('Methods') }}

   {{ name }} defines the following methods.

   .. autosummary::
      :nosignatures:
      :template: function.rst
   {% for item in methods if not item.startswith('_') and not item in inherited_members %}
      ~{{ name }}.{{ item }}
   {%- endfor -%}
   {%- endif -%}
   {%- endblock %}

   {% block attributes -%}
   {%- if attributes -%}
   .. rubric:: {{ _('Attributes') }}

   {{ name }} contains the following attributes.

   .. autosummary::
   {%- for item in attributes if not item.startswith('_') and not item in inherited_members %}
      ~{{ name }}.{{ item }}
   {%- endfor -%}
   {%- endif -%}
   {%- endblock %}
