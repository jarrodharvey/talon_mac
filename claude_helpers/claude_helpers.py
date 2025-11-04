"""
Claude Helper Functions and Actions

This module provides helper functions and actions for Claude Code integration,
including the Talon troubleshooter and other development utilities.
"""

import os
from datetime import datetime
from talon import Module, actions, app, screen
from .talon_troubleshooter import troubleshooter, test_cubes_in_moonlight, test_command_in_app

mod = Module()
mod.tag("claude_helpers", desc="Claude helper functions and troubleshooting tools")

@mod.action_class
class Actions:
    def test_cubes_in_moonlight(target_name: str = None):
        """Test cubes functionality in Moonlight application"""
        return test_cubes_in_moonlight(target_name)
    
    def test_command_in_app(app_name: str, command: str, description: str = ""):
        """Test arbitrary Talon command in specified application"""
        return test_command_in_app(app_name, command, description)
    
    def test_command_with_words(command_word: str, app_word: str):
        """Test command constructed from words - workaround for Talon string limitations"""
        command = f"actions.user.{command_word}()"
        description = f"Test {command_word} command"
        return test_command_in_app(app_word, command, description)
    
    def troubleshooter():
        """Access the global troubleshooter instance"""
        return troubleshooter
    
    def capture_claude_screenshot(screenshots_dir: str = "/Users/jarrod/.talon/user/jarrod/claude_helpers/screenshots"):
        """Capture a screenshot and save it to the claude_helpers screenshots directory"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(screenshots_dir, exist_ok=True)
            
            # Generate timestamp-based filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"claude_screenshot_{timestamp}.png"
            filepath = os.path.join(screenshots_dir, filename)
            
            # Capture screenshot of main screen
            main_screen = screen.main_screen()
            screenshot = screen.capture_rect(main_screen.rect)
            screenshot.write_file(filepath)
            
            # Notify user of success
            app.notify(f"Screenshot saved: {filename}")
            print(f"Claude screenshot saved to: {filepath}")
            
        except Exception as e:
            error_msg = f"Failed to capture screenshot: {str(e)}"
            app.notify(error_msg)
            print(error_msg)