"""
Pattern detection for pathfinding system.
"""
from talon import Module

mod = Module()

@mod.action_class
class PatternDetectionActions:
    def clear_position_tracking() -> None:
        """Clear all position tracking data (used when starting new navigation)"""
        pass
