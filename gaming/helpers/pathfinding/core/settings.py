"""
Core navigation settings for pathfinding system.

Settings for navigation behavior, timing, proximity detection, and game integration.
"""

from talon import Module

mod = Module()

# Navigation proximity settings
mod.setting(
    "highlight_proximity_x",
    type=int,
    default=100,
    desc="Horizontal distance in pixels to stop navigation when highlight is close to target text"
)

mod.setting(
    "highlight_proximity_y", 
    type=int,
    default=80,
    desc="Vertical distance in pixels to stop navigation when highlight is close to target text"
)

mod.setting(
    "highlight_image", 
    type=str,
    default="apple_logo.png",
    desc="Image file name for the highlight box to track in the menu (e.g., 'apple_logo.png')"
)

# Navigation timing and behavior
mod.setting(
    "navigation_interval",
    type=int,
    default=500,
    desc="Interval in milliseconds between navigation steps"
)

mod.setting(
    "navigation_mode",
    type=str,
    default="unified",
    desc="Navigation mode: 'unified' (X/Y proximity), 'vertical' (prioritize vertical), 'horizontal' (prioritize horizontal), 'grid' (column-first grid navigation)"
)

mod.setting(
    "game_action_button",
    type=str,
    default="space",
    desc="Button to press when selecting/activating menu items after navigation"
)

mod.setting(
    "uses_wasd",
    type=bool,
    default=True,
    desc="Use WASD keys for navigation instead of arrow keys"
)

# Grid navigation settings
mod.setting(
    "grid_column_threshold",
    type=int,
    default=150,
    desc="Horizontal distance threshold to determine if two items are in the same column"
)

mod.setting(
    "grid_row_threshold", 
    type=int,
    default=50,
    desc="Vertical distance threshold to determine if two items are in the same row"
)

# Position tracking and stability
mod.setting(
    "position_stability_threshold",
    type=int,
    default=1400,
    desc="Time in milliseconds cursor must remain at position to be considered stable/settled (should be 2x navigation interval)"
)

# Template matching settings
mod.setting(
    "cursor_directory",
    type=str,
    default="",
    desc="Name of cursor directory under cursors/ containing game-specific cursor templates (e.g., 'chained_echoes')"
)

# OCR and text matching settings
mod.setting(
    "menu_enable_fuzzy_matching",
    type=bool,
    default=True,
    desc="Enable fuzzy text matching when exact matches are not found"
)

mod.setting(
    "menu_fuzzy_threshold",
    type=float,
    default=0.6,
    desc="Similarity threshold for fuzzy text matching (0.0-1.0, higher = more strict)"
)