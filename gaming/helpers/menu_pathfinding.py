"""
Menu navigation using OCR text detection and image template matching.
Designed for games that don't support mouse input but have keyboard-based menu navigation.
"""

from talon import Module, actions, app, cron, settings
import os

mod = Module()

# Path to images for template matching
images_to_click_location = "/Users/jarrod/.talon/user/jarrod/gaming/images_to_click/"

# Global variables for navigation job
navigation_job = None
navigation_steps_taken = 0
last_direction_pressed = None

# Settings for menu navigation
mod.setting(
    "highlight_proximity_x",
    type=int,
    default=75,
    desc="Horizontal distance in pixels to stop navigation when highlight is close to target text"
)

mod.setting(
    "highlight_proximity_y", 
    type=int,
    default=55,
    desc="Vertical distance in pixels to stop navigation when highlight is close to target text"
)

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
    desc="Navigation mode: 'unified' (X/Y proximity), 'vertical' (prioritize vertical with tight Y check)"
)

mod.setting(
    "game_action_button",
    type=str,
    default="space",
    desc="Button to press when selecting/activating menu items after navigation"
)

@mod.action_class
class MenuPathfindingActions:
    def test_navigate_to_text_with_highlight(target_text: str, highlight_image: str = "apple_logo.png"):
        """Test function: Navigate using coordinates of text vs highlight image"""
        try:
            print(f"Looking for text: {target_text}")
            
            # Get coordinates of highlight image using existing function
            highlight_coords = actions.user.mouse_helper_find_template_relative(
                f"{images_to_click_location}{highlight_image}"
            )
            if not highlight_coords:
                print(f"Could not find highlight image: {highlight_image}")
                return False
                
            # Get center coordinates of first match
            highlight_rect = highlight_coords[0]
            highlight_center = (highlight_rect.x + highlight_rect.width//2, highlight_rect.y + highlight_rect.height//2)
            print(f"Found highlight image at: {highlight_center}")
            
            # For testing, simulate text coordinates - let's say "Claude" is at position (300, 100)
            text_coords = (300, 100)
            print(f"Simulated text '{target_text}' at: {text_coords}")
            
            # Calculate which direction to move (using WASD)
            text_x, text_y = text_coords
            highlight_x, highlight_y = highlight_center
            
            x_diff = text_x - highlight_x
            y_diff = text_y - highlight_y
            
            print(f"Differences - X: {x_diff}, Y: {y_diff}")
            
            # Determine direction and press appropriate key
            if abs(x_diff) > abs(y_diff):
                # Horizontal movement needed
                if x_diff > 0:
                    print("Moving right (d)")
                    actions.key("d")
                else:
                    print("Moving left (a)")
                    actions.key("a")
            else:
                # Vertical movement needed  
                if y_diff > 0:
                    print("Moving down (s)")
                    actions.key("s")
                else:
                    print("Moving up (w)")
                    actions.key("w")
                    
            return True
            
        except Exception as e:
            print(f"Test navigation error: {str(e)}")
            return False

    def get_text_coordinates(target_text: str):
        """Test function to find coordinates of text using OCR"""
        try:
            # Disconnect eye tracker to scan full screen
            actions.user.disconnect_ocr_eye_tracker()
            
            # Trigger OCR scan without visual overlay
            
            # Try different approaches to access the OCR controller
            import sys
            gaze_ocr_controller = None
            
            # Method 1: Check sys.modules for loaded gaze_ocr_talon
            for module_name, module in sys.modules.items():
                if 'gaze_ocr' in module_name and hasattr(module, 'gaze_ocr_controller'):
                    gaze_ocr_controller = module.gaze_ocr_controller
                    print(f"Found gaze_ocr_controller via sys.modules in: {module_name}")
                    break
            
            # Method 2: Try accessing through globals 
            if not gaze_ocr_controller:
                import builtins
                if hasattr(builtins, 'gaze_ocr_controller'):
                    gaze_ocr_controller = builtins.gaze_ocr_controller
                    print("Found gaze_ocr_controller in builtins")
            
            # Method 3: Try direct import approach
            if not gaze_ocr_controller:
                try:
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(
                        "gaze_ocr_talon", 
                        "/Users/jarrod/.talon/user/talon-gaze-ocr/gaze_ocr_talon.py"
                    )
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        # Don't execute - just see if we can access existing instance
                        print("Could load module spec, but need existing instance")
                except Exception as e:
                    print(f"Import approach failed: {e}")
            
            if gaze_ocr_controller:
                # Trigger OCR scan without overlay
                gaze_ocr_controller.read_nearby()
                
                # Get the latest screen contents
                contents = gaze_ocr_controller.latest_screen_contents()
                print(f"Got OCR contents with {len(contents.result.lines)} lines")
                
                # Search for the target text
                for line_idx, line in enumerate(contents.result.lines):
                    for word_idx, word in enumerate(line.words):
                        print(f"Line {line_idx}, Word {word_idx}: '{word.text}' at ({word.left}, {word.top})")
                        if target_text.lower() in word.text.lower():
                            coords = (word.left + word.width//2, word.top + word.height//2)
                            print(f"Found '{target_text}' at coordinates: {coords}")
                            print(f"Word bounds: left={word.left}, top={word.top}, width={word.width}, height={word.height}")
                            
                            # Reconnect eye tracker
                            actions.user.connect_ocr_eye_tracker()
                            return coords
                
                print(f"Text '{target_text}' not found in OCR results")
            else:
                print("Could not find gaze_ocr_controller via any method")
            
            # Reconnect eye tracker
            actions.user.connect_ocr_eye_tracker()
            return None
            
        except Exception as e:
            print(f"Error getting text coordinates: {str(e)}")
            actions.user.connect_ocr_eye_tracker()
            return None

    def navigate_to_text_with_highlight(target_text: str, highlight_image: str, use_wasd: bool = False):
        """Navigate menu highlight box toward target text using coordinates"""
        try:
            # Get text coordinates using OCR
            text_coords = actions.user.get_text_coordinates(target_text)
            if not text_coords:
                app.notify(f"Could not find text: {target_text}")
                return False
            
            # Get coordinates of highlight image using existing function
            highlight_coords = actions.user.mouse_helper_find_template_relative(
                f"{images_to_click_location}{highlight_image}"
            )
            if not highlight_coords:
                app.notify(f"Could not find highlight image: {highlight_image}")
                return False
                
            # Get center coordinates of first match
            highlight_rect = highlight_coords[0]
            highlight_center = (highlight_rect.x + highlight_rect.width//2, highlight_rect.y + highlight_rect.height//2)
            
            # Calculate which direction to move
            text_x, text_y = text_coords
            highlight_x, highlight_y = highlight_center
            
            x_diff = text_x - highlight_x
            y_diff = text_y - highlight_y
            
            print(f"Differences - X: {x_diff}, Y: {y_diff}")
            
            # Determine direction and press appropriate key
            if abs(x_diff) > abs(y_diff):
                if x_diff > 0:
                    if use_wasd:
                        print("Moving right (d)")
                        actions.key("d")
                    else:
                        print("Moving right (→)")
                        actions.key("right")
                else:
                    if use_wasd:
                        print("Moving left (a)")
                        actions.key("a")
                    else:
                        print("Moving left (←)")
                        actions.key("left")
            else:
                if y_diff > 0:
                    if use_wasd:
                        print("Moving down (s)")
                        actions.key("s")
                    else:
                        print("Moving down (↓)")
                        actions.key("down")
                else:
                    if use_wasd:
                        print("Moving up (w)")
                        actions.key("w")
                    else:
                        print("Moving up (↑)")
                        actions.key("up")
                    
            return True
            
        except Exception as e:
            app.notify(f"Navigation error: {str(e)}")
            return False

    def navigate_to_text_with_highlight_wasd(target_text: str, highlight_image: str):
        """Navigate using WASD keys - convenience function"""
        return actions.user.navigate_to_text_with_highlight(target_text, highlight_image, True)

    def navigate_to_text_with_highlight_arrows(target_text: str, highlight_image: str):
        """Navigate using arrow keys - convenience function"""
        return actions.user.navigate_to_text_with_highlight(target_text, highlight_image, False)

    def calculate_distance(pos1: tuple, pos2: tuple) -> float:
        """Calculate distance between two coordinate points"""
        x_diff = pos1[0] - pos2[0]
        y_diff = pos1[1] - pos2[1]
        return (x_diff ** 2 + y_diff ** 2) ** 0.5

    def navigate_step(target_text: str, highlight_image: str, use_wasd: bool, max_steps: int = None, extra_step: bool = False, action_button: str = None) -> bool:
        """Single navigation step - check proximity and move if needed"""
        global navigation_steps_taken, last_direction_pressed
        
        # Check max steps limit
        if max_steps is not None and navigation_steps_taken >= max_steps:
            print(f"Reached maximum steps limit: {max_steps}")
            actions.user.stop_continuous_navigation()
            return True
            
        try:
            # Get current coordinates
            text_coords = actions.user.get_text_coordinates(target_text)
            if not text_coords:
                print(f"Could not find text: {target_text}")
                actions.user.stop_continuous_navigation()
                return False

            highlight_coords = actions.user.mouse_helper_find_template_relative(
                f"{images_to_click_location}{highlight_image}"
            )
            if not highlight_coords:
                print(f"Could not find highlight image: {highlight_image} - stopping navigation")
                actions.user.stop_continuous_navigation()
                return False
            
            print(f"Found {len(highlight_coords)} highlight matches")

            # Calculate positions
            highlight_rect = highlight_coords[0]
            highlight_center = (highlight_rect.x + highlight_rect.width//2, highlight_rect.y + highlight_rect.height//2)
            
            # Check proximity using configurable navigation mode
            x_diff = text_coords[0] - highlight_center[0]
            y_diff = text_coords[1] - highlight_center[1]
            navigation_mode = settings.get("user.navigation_mode")
            
            print(f"Text coords: {text_coords}, Highlight coords: {highlight_center}")
            print(f"X diff: {x_diff:.1f}, Y diff: {y_diff:.1f}, Mode: {navigation_mode}")
            
            if navigation_mode == "vertical":
                # Original vertical logic - tight Y check only
                is_on_target = abs(y_diff) <= 25
                print(f"Vertical mode - Y close: {abs(y_diff) <= 25}, On target: {is_on_target}")
            else:
                # Unified mode - both X and Y proximity
                proximity_x = settings.get("user.highlight_proximity_x")
                proximity_y = settings.get("user.highlight_proximity_y")
                x_close = abs(x_diff) <= proximity_x
                y_close = abs(y_diff) <= proximity_y
                is_on_target = x_close and y_close
                print(f"Unified mode - X close: {x_close}, Y close: {y_close}, On target: {is_on_target}")
            
            if is_on_target:
                if action_button:
                    print(f"Reached target! Pressing action button: {action_button}")
                    actions.key(action_button)
                    actions.user.stop_continuous_navigation()
                    return True
                elif extra_step and last_direction_pressed:
                    print(f"Reached target! Taking extra step with {last_direction_pressed}")
                    actions.key(last_direction_pressed)
                    actions.user.stop_continuous_navigation()
                    return True
                else:
                    print(f"Reached target!")
                    actions.user.stop_continuous_navigation()
                    return True

            # Calculate direction and move - use the differences already calculated above
            print(f"Continuing navigation - X diff: {x_diff:.1f}, Y diff: {y_diff:.1f}")
            
            if navigation_mode == "vertical":
                # Vertical mode - prioritize vertical movement
                if abs(y_diff) > 10:  # Prioritize vertical if more than 10px away
                    if y_diff > 0:
                        key_to_press = "s" if use_wasd else "down"
                        print(f"Pressing {key_to_press} (down) - vertical priority")
                        actions.key(key_to_press)
                        last_direction_pressed = key_to_press
                    else:
                        key_to_press = "w" if use_wasd else "up"
                        print(f"Pressing {key_to_press} (up) - vertical priority")
                        actions.key(key_to_press)
                        last_direction_pressed = key_to_press
                else:
                    # Only move horizontally when vertically aligned
                    if x_diff > 0:
                        key_to_press = "d" if use_wasd else "right"
                        print(f"Pressing {key_to_press} (right) - vertical aligned")
                        actions.key(key_to_press)
                        last_direction_pressed = key_to_press
                    else:
                        key_to_press = "a" if use_wasd else "left"
                        print(f"Pressing {key_to_press} (left) - vertical aligned")
                        actions.key(key_to_press)
                        last_direction_pressed = key_to_press
            else:
                # Unified mode - move in direction with larger difference
                if abs(x_diff) > abs(y_diff):
                    if x_diff > 0:
                        key_to_press = "d" if use_wasd else "right"
                        print(f"Pressing {key_to_press} (right)")
                        actions.key(key_to_press)
                        last_direction_pressed = key_to_press
                    else:
                        key_to_press = "a" if use_wasd else "left"
                        print(f"Pressing {key_to_press} (left)")
                        actions.key(key_to_press)
                        last_direction_pressed = key_to_press
                else:
                    if y_diff > 0:
                        key_to_press = "s" if use_wasd else "down"
                        print(f"Pressing {key_to_press} (down)")
                        actions.key(key_to_press)
                        last_direction_pressed = key_to_press
                    else:
                        key_to_press = "w" if use_wasd else "up"
                        print(f"Pressing {key_to_press} (up)")
                        actions.key(key_to_press)
                        last_direction_pressed = key_to_press
            
            # Increment step counter
            navigation_steps_taken += 1        
            return False  # Continue navigation
            
        except Exception as e:
            print(f"Navigation step error: {str(e)}")
            actions.user.stop_continuous_navigation()
            return False

    def start_continuous_navigation(target_text: str, highlight_image: str, use_wasd: bool = False, max_steps: int = None, extra_step: bool = False, action_button: str = None) -> None:
        """Start continuous navigation with cron job until target reached or game_stop called"""
        global navigation_job, navigation_steps_taken, last_direction_pressed
        
        # Stop any existing navigation
        actions.user.stop_continuous_navigation()
        
        # Reset step counter and direction tracking
        navigation_steps_taken = 0
        last_direction_pressed = None
        
        # Start new navigation job
        navigation_interval = settings.get("user.navigation_interval")
        navigation_job = cron.interval(
            f"{navigation_interval}ms", 
            lambda: actions.user.navigate_step(target_text, highlight_image, use_wasd, max_steps, extra_step, action_button)
        )
        max_steps_text = f" (max {max_steps} steps)" if max_steps else ""
        action_text = f" (will press '{action_button}')" if action_button else ""
        print(f"Started continuous navigation to '{target_text}'{action_text} every {navigation_interval}ms{max_steps_text}")

    def stop_continuous_navigation() -> None:
        """Stop continuous navigation job"""
        global navigation_job
        if navigation_job:
            cron.cancel(navigation_job)
            navigation_job = None
            print("Stopped continuous navigation")

    def navigate_continuously(target_text: str, highlight_image: str, use_wasd: bool = True, max_steps: int = None, extra_step: bool = False, action_button: str = None) -> None:
        """Start continuous navigation with configurable input method and behavior"""
        actions.user.start_continuous_navigation(target_text, highlight_image, use_wasd, max_steps, extra_step, action_button)

    # Backwards compatibility wrappers
    def navigate_continuously_wasd(target_text: str, highlight_image: str, action_button: str = None) -> None:
        """Start continuous navigation using WASD keys"""
        actions.user.navigate_continuously(target_text, highlight_image, True, None, False, action_button)

    def navigate_continuously_arrows(target_text: str, highlight_image: str, action_button: str = None) -> None:
        """Start continuous navigation using arrow keys"""
        actions.user.navigate_continuously(target_text, highlight_image, False, None, False, action_button)

    def navigate_continuously_wasd_extra(target_text: str, highlight_image: str, max_steps: int = None, action_button: str = None) -> None:
        """Start continuous navigation using WASD keys with extra step"""
        actions.user.navigate_continuously(target_text, highlight_image, True, max_steps, True, action_button)

    def navigate_continuously_arrows_extra(target_text: str, highlight_image: str, action_button: str = None) -> None:
        """Start continuous navigation using arrow keys with extra step"""
        actions.user.navigate_continuously(target_text, highlight_image, False, None, True, action_button)



    def navigate_to_word(word: str, highlight_image: str = "chained_hand.png", use_wasd: bool = True, max_steps: int = None, action_button: str = None, use_configured_action: bool = False) -> None:
        """Navigate to any word found via OCR with configurable input method and action"""
        # Convert word to proper case for OCR matching
        target_text = word.capitalize()
        
        # Use configured action button if requested
        if use_configured_action:
            action_button = settings.get("user.game_action_button")
        
        # Print appropriate message
        if action_button:
            print(f"Navigating to word: '{target_text}' and selecting with '{action_button}'")
        else:
            print(f"Navigating to word: '{target_text}' using configurable navigation system")
            
        actions.user.start_continuous_navigation(target_text, highlight_image, use_wasd, max_steps, False, action_button)

    # Backwards compatibility wrappers
    def navigate_to_word_wasd(word: str, highlight_image: str = "chained_hand.png", max_steps: int = None, action_button: str = None) -> None:
        """Navigate to any word found via OCR using WASD, optionally pressing action button when reached"""
        actions.user.navigate_to_word(word, highlight_image, True, max_steps, action_button, False)

    def navigate_to_word_wasd_with_action(word: str, highlight_image: str = "chained_hand.png") -> None:
        """Navigate to any word found via OCR using WASD and press the configured action button"""
        actions.user.navigate_to_word(word, highlight_image, True, None, None, True)


    def test_continuous_navigation(target_text: str, highlight_image: str, max_steps: int = 3, use_wasd: bool = False, countdown: int = 0) -> None:
        """Test continuous navigation with limited steps for safety"""
        if countdown > 0:
            print(f"Starting navigation to '{target_text}' in {countdown} seconds...")
            actions.sleep(f"{countdown}s")
        actions.user.navigate_continuously(target_text, highlight_image, use_wasd, max_steps)