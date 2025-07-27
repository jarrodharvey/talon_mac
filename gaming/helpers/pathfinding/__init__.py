"""
Pathfinding module for voice-controlled menu navigation.

This module provides OCR-based navigation, template matching, and cube-based
UI element selection for keyboard-only games and applications.
"""

# Import all submodules to maintain backward compatibility
from . import core
from . import ocr
from . import cubes
from . import debug
from . import utils

# Re-export key functions for backward compatibility
# Import key action functions that external code depends on
try:
    # These imports will work as modules are completed
    from .core.navigation import CoreNavigationActions
    from .ocr.text_detection import OCRTextDetectionActions
    from .ocr.template_matching import TemplateMatchingActions
    from .utils.geometry import GeometryActions
    from .utils.action_helpers import ActionHelpersActions
except ImportError as e:
    print(f"Note: Some pathfinding modules still being migrated: {e}")

__all__ = [
    'core',
    'ocr', 
    'cubes',
    'debug',
    'utils'
]