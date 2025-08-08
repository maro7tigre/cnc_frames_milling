"""
G-Code IDE Module

This module provides G-code editing capabilities with syntax highlighting,
line numbers, error indication, and L-code variable support.
"""

from .gcode_editor import GCodeEditor, GCodeSyntaxHighlighter, LineNumberArea

__all__ = ['GCodeEditor', 'GCodeSyntaxHighlighter', 'LineNumberArea']