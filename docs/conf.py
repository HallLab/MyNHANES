# # Configuration file for the Sphinx documentation builder.
# #
# # For the full list of built-in configuration values, see the documentation:
# # https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information ----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
import sphinx_rtd_theme

# -- Project information -----------------------------------------------------
project = 'MyNHANES'
copyright = '2024, Andre Rico'
author = "Andre Rico"
release = "0.2.0"
version = "0.2.0"

# -- General configuration --------------------------------------------------
# sphinx-doc.org/en/master/usage/configuration.html#general-configuration
# Sphinx estensions
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.todo',
    sphinx_rtd_theme
    # "sphinx.ext.autosectionlabel",
    # "sphinx.ext.intersphinx",
]

# This is used by Read the Docs to customize the build directory
on_rtd = os.environ.get('READTHEDOCS') == 'True'

if on_rtd:
    build_dir = os.environ.get('READTHEDOCS_OUTPUT', '')
    html_build_dir = os.path.join(build_dir, 'html')
else:
    build_dir = '_build'
    html_build_dir = '_build/html'
    print("Building locally, output path is '_build/html'")
    django_project_dir = os.path.abspath('../mynhanes')
    sys.path.insert(0, django_project_dir)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'project.settings'
    import django
    django.setup()

print(f'O diretorio sera: {html_build_dir}')

# -- Options for HTML output ------------------------------------------------
# www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# # The theme to use for HTML and HTML Help pages.  See the documentation for
# html_theme = 'alabaster'
# html_theme = "cloud"
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
# html_logo = "_static/pictures/logo.jpg"
master_doc = 'index'
templates_path = ["_templates"]
# exclude_patterns = []
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
