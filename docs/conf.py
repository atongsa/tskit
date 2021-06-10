#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config
# -- Path setup --------------------------------------------------------------
# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import subprocess
import sys
from unittest.mock import MagicMock

from docutils import nodes
from sphinx import addnodes
from sphinx.util.docfields import TypedField

# It's easier not to try to build the low-level module for the
# documentation build on readthedocs, so we mock the module. Follows
# the recommended pattern at
# http://docs.readthedocs.org/en/latest/faq.html


class Mock(MagicMock):
    @classmethod
    def __getattr__(cls, name):
        return MagicMock()


MOCK_MODULES = ["_tskit"]
sys.modules.update((mod_name, Mock()) for mod_name in MOCK_MODULES)


sys.path.insert(0, os.path.abspath("../python"))

read_the_docs_build = os.environ.get("READTHEDOCS", None) == "True"
if read_the_docs_build:
    subprocess.call("cd doxygen; doxygen", shell=True)


# -- Project information -----------------------------------------------------

project = "tskit"
copyright = "2018-2021, Tskit developers"  # noqa: A001
author = "Tskit developers"


tskit_version = None
with open(os.path.abspath("../python/tskit/_version.py")) as f:
    exec(f.read())
# tskit_version is defined in the specified file.
release = tskit_version
version = ".".join(release.split(".")[:2])

###################################################################
#
# Monkey-patching sphinx to workaround really annoying bug in ivar
# handling. See
# https://stackoverflow.com/questions/31784830
#


def patched_make_field(self, types, domain, items, env):
    # type: (list, str, tuple) -> nodes.field
    def handle_item(fieldarg, content):
        par = nodes.paragraph()
        par += addnodes.literal_strong("", fieldarg)  # Patch: this line added
        # par.extend(self.make_xrefs(self.rolename, domain, fieldarg,
        #                           addnodes.literal_strong))
        if fieldarg in types:
            par += nodes.Text(" (")
            # NOTE: using .pop() here to prevent a single type node to be
            # inserted twice into the doctree, which leads to
            # inconsistencies later when references are resolved
            fieldtype = types.pop(fieldarg)
            if len(fieldtype) == 1 and isinstance(fieldtype[0], nodes.Text):
                typename = "".join(n.astext() for n in fieldtype)
                par.extend(
                    self.make_xrefs(
                        self.typerolename, domain, typename, addnodes.literal_emphasis
                    )
                )
            else:
                par += fieldtype
            par += nodes.Text(")")
        par += nodes.Text(" -- ")
        par += content
        return par

    fieldname = nodes.field_name("", self.label)
    if len(items) == 1 and self.can_collapse:
        fieldarg, content = items[0]
        bodynode = handle_item(fieldarg, content)
    else:
        bodynode = self.list_type()
        for fieldarg, content in items:
            bodynode += nodes.list_item("", handle_item(fieldarg, content))
    fieldbody = nodes.field_body("", bodynode)
    return nodes.field("", fieldname, fieldbody)


TypedField.make_field = patched_make_field

###################################################################


# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.todo",
    "breathe",
    "sphinxarg.ext",
    "sphinx_issues",
    "autodocsumm",
]

# Github repo
issues_github_path = "tskit-dev/tskit"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = None


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Options for sphinx_rtd_theme. See
# https://docs.readthedocs.io/en/stable/guides/vcs.html#github
html_context = {
    "display_github": True,  # Integrate GitHub
    "github_user": "tskit-dev",
    "github_repo": "tskit",  # Repo name
    "github_version": "main",  # Version
    "conf_py_path": "/docs/",  # Path in the checkout to the docs root
}

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
# html_sidebars = {}

html_logo = "_static/tskit_logo_pale.svg"

# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "tskitdoc"


# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',
    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, "tskit.tex", "tskit Documentation", "Tskit developers", "manual"),
]


# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, "tskit", "tskit Documentation", [author], 1)]


# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "tskit",
        "tskit Documentation",
        author,
        "tskit",
        "One line description of project.",
        "Miscellaneous",
    ),
]


# -- Options for Epub output -------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ''

# A unique identification for the text.
#
# epub_uid = ''

# A list of files that should not be packed into the epub file.
epub_exclude_files = ["search.html"]


# -- Extension configuration -------------------------------------------------

# -- Options for intersphinx extension ---------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    "https://docs.python.org/3": None,
    "https://numpy.org/doc/stable/": None,
    "https://svgwrite.readthedocs.io/en/stable/": None,
    "tutorials": ("https://tskit.dev/tutorials/", None),
}

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# Breath extension lets us include doxygen C documentation.
breathe_projects = {"tskit": "doxygen/xml"}
breathe_default_project = "tskit"
breathe_domain_by_extension = {"h": "c"}
breathe_show_define_initializer = True

# TODO add an RST epilogue defining the version numbers of the Python
# and C APIs. Should be simple to do the Python version. Getting C
# will probably mean parsing the doxygen XML.

nitpicky = True
nitpick_ignore = [
    ("c:identifier", "int32_t"),
    ("c:identifier", "uint32_t"),
    ("c:identifier", "FILE"),
    ("c:type", "int32_t"),
    ("c:type", "uint32_t"),
    ("c:type", "bool"),
    ("py:class", "tskit.metadata.AbstractMetadataCodec"),
    ("py:class", "tskit.trees.Site"),
    # TODO these have been triaged here to make the docs compile, but we should
    # sort them out properly. https://github.com/tskit-dev/tskit/issues/336
    ("py:class", "array_like"),
    ("py:class", "row-like"),
    ("py:class", "array-like"),
    ("py:class", "dtype=np.uint32"),
    ("py:class", "dtype=np.uint32."),
    ("py:class", "dtype=np.int32"),
    ("py:class", "dtype=np.int8"),
    ("py:class", "dtype=np.float64"),
    ("py:class", "dtype=np.int64"),
]
