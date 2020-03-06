# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import mlx.traceability
from pkg_resources import get_distribution

# -- Path setup --------------------------------------------------------------
# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
# sys.path.insert(0, os.path.abspath('../mlx'))

# -- Project information -----------------------------------------------------

project = 'mlx.robot2rst'
copyright = '2020, Jasper Craeghs'
authors = ['Stein Heselmans', 'Jasper Craeghs']

# The full version, including alpha/beta/rc tags
release = get_distribution('mlx.robot2rst').version
version = '.'.join(release.split('.')[:2])

man_pages = [
    ('index', 'robot2rst', 'Script to convert .robot files to .rst files with traceable items',
     authors, 1)
]

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'mlx.traceability',
]

traceability_relationships = {
    'validates': 'validated_by',
    'ext_toolname': '',
}
traceability_relationship_to_string = {
    'validates': 'Validates',
    'validated_by': 'Validated by',
    'ext_toolname': 'Reference to toolname'
}
traceability_external_relationship_to_url = {
    'ext_toolname': 'http://toolname.company.com/my_lib/system-requirements.html#field1'
}
traceability_render_relationship_per_item = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = [os.path.join(os.path.dirname(mlx.traceability.__file__), 'assets')]


def setup(app):
    pass
