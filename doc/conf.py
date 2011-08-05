# -*- coding: utf-8 -*-
#
# django-configglue documentation build configuration file
#

import sys
import os

# import django_configglue, to introspect the version string
sys.path.insert(0, os.path.abspath('..'))
import django_configglue

# -- General configuration -----------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = ['sphinx.ext.autodoc']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The encoding of source files.
source_encoding = 'utf-8'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'django-configglue'
copyright = u'Ricardo Kirkner'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = django_configglue.__version__
# The full version, including alpha/beta/rc tags.
release = django_configglue.__version__

# List of directories, relative to source directory, that shouldn't be searched
# for source files.
exclude_trees = ['_build']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
modindex_common_prefix = ['django_configglue.']


# -- Options for HTML output ---------------------------------------------------

# The theme to use for HTML and HTML Help pages.  Major themes that come with
# Sphinx are currently 'default' and 'sphinxdoc'.
html_theme = 'default'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Output file base name for HTML help builder.
htmlhelp_basename = 'django-configgluedoc'


# -- Options for LaTeX output --------------------------------------------------

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
  ('index', 'django-configglue.tex', u'django-configglue Documentation',
   u'Ricardo Kirkner', 'manual'),
]
