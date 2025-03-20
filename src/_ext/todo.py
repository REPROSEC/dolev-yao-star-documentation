from __future__ import annotations

from docutils import nodes

from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective, SphinxRole
from sphinx.util.typing import ExtensionMetadata
from docutils.parsers.rst import directives

class TodoRole(SphinxRole):

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        node = nodes.inline(text=f'TODO: {self.text}',classes=["todo-inline"])
        return [node], []

def setup(app: Sphinx) -> ExtensionMetadata:
   app.add_role('todo', TodoRole())

   return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
