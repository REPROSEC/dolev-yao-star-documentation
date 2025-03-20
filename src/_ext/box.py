from __future__ import annotations

from docutils import nodes

from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective, SphinxRole
from sphinx.util.typing import ExtensionMetadata
from docutils.parsers.rst import directives

class RevealDirective(SphinxDirective):
    
     required_arguments = 0
     optional_arguments = 0
     has_content = True

     option_spec = {'header': directives.unchanged}
     
     def run(self) -> list[nodes.Node]:

         header = self.options.get('header')

         header_node = nodes.container(classes = ["toggle-header"])
         
         header_inner = nodes.strong(text = header)
         header_paragraph = nodes.paragraph('')
         header_paragraph.children = [header_inner]

         header_node.children = [header_paragraph]
         
         content_node = nodes.container(classes=["toggle-content box"])
         self.state.nested_parse(self.content, self.content_offset,
                                 content_node)
         return [header_node, content_node]


class AnswerDirective(SphinxDirective):

     required_arguments = 0
     has_content = True

     def run(self) -> list[nodes.Node]:
         header_node = nodes.container(classes = ["toggle-header"])
         
         header_inner = nodes.strong(text = "Show/Hide Answer")
         header_paragraph = nodes.paragraph('')
         header_paragraph.children = [header_inner]

         header_node.children = [header_paragraph]
         
         content_node = nodes.container(classes=["toggle-content"])
         self.state.nested_parse(self.content, self.content_offset,
                                 content_node)
         return [header_node, content_node]
          
    

def setup(app: Sphinx) -> ExtensionMetadata:
    app.add_directive('reveal', RevealDirective)
    app.add_directive('toggle-answer', AnswerDirective)

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
