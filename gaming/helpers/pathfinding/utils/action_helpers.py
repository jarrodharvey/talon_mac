"""
Action helper functions for pathfinding system.

Contains utilities for button pressing, action timing, and input handling.
"""

from talon import Module, actions

mod = Module()

def press_action_button_multiple(button: str, count: int = 1, interval: float = 0.1):
    """Press action button multiple times with configurable interval"""
    for i in range(count):
        actions.key(button)
        if i < count - 1:  # Don't sleep after last press
            actions.sleep(f"{interval}s")

@mod.action_class
class ActionHelpersActions:
    def press_action_button_multiple(button: str, count: int = 1, interval: float = 0.1):
        """Press action button multiple times with configurable interval"""
        press_action_button_multiple(button, count, interval)