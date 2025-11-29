"""
Mermaid diagram language support.
Provides voice commands for creating flowcharts, sequence diagrams, etc.
"""
from talon import Context, Module, actions

mod = Module()
ctx = Context()

# Activate this context when language is "mermaid"
ctx.matches = r"""
code.language: mermaid
"""

# Override code actions for Mermaid-specific behavior
@ctx.action_class("user")
class MermaidActions:
    def code_comment_line():
        """Line comment for Mermaid"""
        actions.insert("%% ")
