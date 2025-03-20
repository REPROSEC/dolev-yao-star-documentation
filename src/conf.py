# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
from pathlib import Path

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Security Analysis of Cryptographic Protocols with DY*'
copyright = '2025, DY* Maintainer'
author = 'DY* Maintainer'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

sys.path.append(str(Path('_ext').resolve()))

extensions = ['sphinxcontrib.contentui'
              , 'box'
              , 'my_admonitions'
              , 'todo'
              ]

templates_path = ['templates']
exclude_patterns = ['build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
# html_theme = 'furo'
html_static_path = ['../static']

html_css_files = ['css/remember.css'
                  , 'css/example.css'
                  , 'css/exercise.css'
                  , 'css/infobox.css'
                  , 'css/box.css'
                  , 'css/todo.css'
                  , 'css/math.css'
                  ,
                  ]

# setting F* as default highlight language
highlight_language = "fstar"
default_role = "any"

rst_prolog = """
.. role:: fstar(code)
   :language: fstar
   :class: highlight

.. role:: boxx
"""
