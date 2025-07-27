"""
OCR and template matching functionality for pathfinding system.

Handles text detection, template matching, cursor detection, and fuzzy text matching.
"""

from . import text_detection
from . import template_matching
from . import homophones

__all__ = [
    'text_detection',
    'template_matching', 
    'homophones'
]