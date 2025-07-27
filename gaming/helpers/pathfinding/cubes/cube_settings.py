"""
Cube system settings for pathfinding.

All settings related to the visual cube overlay system for UI navigation.
"""

from talon import Module

mod = Module()

# Cube visual appearance settings
mod.setting(
    "cube_background_color",
    type=str,
    default="87CEEB",
    desc="Background color of cube overlay boxes (hex color without #)"
)

mod.setting(
    "cube_stroke_color", 
    type=str,
    default="4682B4",
    desc="Border color of cube overlay boxes (hex color without #)"
)

mod.setting(
    "cube_text_color",
    type=str,
    default="000000", 
    desc="Text color of cube numbers (hex color without #)"
)

mod.setting(
    "cube_text_background_color",
    type=str,
    default="FFFFFF",
    desc="Background color behind cube number text (hex color without #)"
)

mod.setting(
    "cube_transparency",
    type=str,
    default="0x55",
    desc="Transparency level of cube boxes (hex value: 0x00=transparent, 0xFF=opaque)"
)

mod.setting(
    "cube_text_transparency", 
    type=str,
    default="0xCC",
    desc="Transparency level of cube number text (hex value: 0x00=transparent, 0xFF=opaque)"
)

mod.setting(
    "cube_stroke_width",
    type=int,
    default=2,
    desc="Width of cube box borders in pixels"
)

mod.setting(
    "cube_text_size",
    type=int,
    default=16,
    desc="Font size of cube numbers"
)

mod.setting(
    "cube_font",
    type=str,
    default="arial",
    desc="Font family for cube numbers"
)

# Cube behavior settings
mod.setting(
    "cube_min_width",
    type=int,
    default=20,
    desc="Minimum width for UI elements to be shown as cubes"
)

mod.setting(
    "cube_min_height",
    type=int,
    default=15,
    desc="Minimum height for UI elements to be shown as cubes"
)

mod.setting(
    "cube_target_offset_x",
    type=int,
    default=10,
    desc="Horizontal offset from left edge when targeting cube (pixels)"
)

mod.setting(
    "cube_max_count",
    type=int,
    default=99,
    desc="Maximum number of cubes to display"
)

mod.setting(
    "cube_detection_threshold",
    type=float,
    default=0.8,
    desc="Confidence threshold for UI element detection (0.0-1.0)"
)