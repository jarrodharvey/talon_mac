"""
Pathfinding module for voice-controlled menu navigation.

This module provides OCR-based navigation, template matching, and cube-based
UI element selection for keyboard-only games and applications.
"""

# Import all submodules to ensure action classes are registered
from . import core
from . import ocr
from . import cubes
from . import debug
from . import utils

# CRITICAL: Import action classes to ensure they are registered with Talon
# These imports must happen so that @mod.action_class decorators execute
try:
    from .core import navigation
    from .core import pattern_detection
    from .core import settings
    from .ocr import text_detection
    from .ocr import template_matching
    from .ocr import homophones
    from .utils import geometry
    from .utils import action_helpers
    from .cubes import cube_settings
    print("Pathfinding module loaded: all action classes should now be registered")
except ImportError as e:
    print(f"Error loading pathfinding modules: {e}")
    print("Some pathfinding functionality may not be available")

__all__ = [
    'core',
    'ocr', 
    'cubes',
    'debug',
    'utils'
]