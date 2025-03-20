# taken from https://github.com/coderefinery/sphinx-lesson/blob/master/sphinx_lesson/directives.py

from __future__ import annotations

from docutils import nodes

from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective, SphinxRole
from sphinx.util.typing import ExtensionMetadata
from docutils.parsers.rst import directives
from docutils.parsers.rst.directives.admonitions \
  import Admonition as AdmonitionDirective

class BaseAdmonitionDirective(AdmonitionDirective, SphinxDirective):

     required_arguments = 0
     optional_arguments = 1
     has_content = True

     extra_classes = []
     title_prefix = ""
     
     def run(self) -> list[nodes.Node]:
         self.node_class = nodes.admonition
          
         if len(self.arguments) == 0:
              self.arguments = [self.title_prefix]
         elif len(self.title_prefix) == 0:
              self.arguments = [self.arguments[0]]
         else:
              self.arguments = [self.title_prefix + ": " + self.arguments[0]]
              
         ret = super().run()
         ret[0].attributes['classes'] = ['admonition']
         ret[0].attributes['classes'].extend(self.extra_classes)
         return ret

class RememberDirective(BaseAdmonitionDirective):
     extra_classes = ['remember']
     title_prefix = "Remember"

class HowtoDirective(BaseAdmonitionDirective):
     extra_classes = ['remember']
     title_prefix = "How-To"

     
class ExampleDirective(BaseAdmonitionDirective):
     extra_classes = ['example']
     title_prefix = "Example"

class InfoDirective(BaseAdmonitionDirective):
     extra_classes = ['info']

class InfoBoxDirective(BaseAdmonitionDirective):
     extra_classes = ['infobox']
     

class ExerciseDirective(BaseAdmonitionDirective):
     extra_classes = ['exercise']
     title_prefix = "Exercise"

class TodoDirective(BaseAdmonitionDirective):
     extra_classes = ['todo']
     title_prefix = "TODO"


def setup(app: Sphinx) -> ExtensionMetadata:
    app.add_directive('remember', RememberDirective)
    app.add_directive('howto', HowtoDirective)
    app.add_directive('example', ExampleDirective)
    app.add_directive('info', InfoDirective)
    app.add_directive('infobox', InfoBoxDirective)
    app.add_directive('exercise', ExerciseDirective)
    app.add_directive('todo', TodoDirective)

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
