# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from ai_chatter.__about__ import __app_name__, __author__, __version__

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = __app_name__
copyright = f"2023-present, {__author__}"  # noqa: A001
author = __author__
release = __version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx_rtd_theme",
    "sphinxcontrib.cairosvgconverter",
    "sphinxcontrib.plantuml",
    "sphinxcontrib_relativeinclude",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for output ------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-latex-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["assets"]
templates_path = ["_templates"]

latex_elements = {
    "extraclassoptions": "openany,oneside",
    "papersize": "a4paper",
    "pointsize": "12pt",
    "figure_align": "H",
}

# -- Autodoc configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
# https://www.sphinx-doc.org/en/master/usage/extensions/autosummary.html

add_module_names = False

autodoc_mock_imports = ["alembic", "sqlalchemy", "pydantic_settings", "docutils", "sphinx"]
autodoc_member_order = "bysource"

autosummary_context = {
    "project": __app_name__,
    "version": __version__,
}

# def setup(app):
#     """Register the directive."""
#     app.add_directive("relativeinclude", RelativeInclude)
