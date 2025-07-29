"""
Core navigation logic for pathfinding system.

Contains the main navigation algorithms including step-by-step navigation,
continuous navigation, and navigation mode handling.
"""

from talon import Module, actions, settings, cron
from ..utils.action_helpers import press_action_button_multiple

mod = Module()

# Global variables for navigation job tracking
navigation_job = None
navigation_steps_taken = 0
last_direction_pressed = None
cursor_position_history = []

def find_currently_selected_word(cursor_pos):
    """Find the currently selected word by looking for text to the RIGHT of cursor position"""
    try:
        # Get OCR data using same method as get_text_coordinates
        import sys
        gaze_ocr_controller = None
        
        # Find the OCR controller
        for module_name, module in sys.modules.items():
            if 'gaze_ocr' in module_name and hasattr(module, 'gaze_ocr_controller'):
                gaze_ocr_controller = module.gaze_ocr_controller
                break
        
        if not gaze_ocr_controller:
            print("ERROR: Could not find gaze_ocr_controller for selected word detection")
            return None
            
        # Get the latest OCR scan (should already be available from recent navigation)
        contents = gaze_ocr_controller.latest_screen_contents()
        if not contents or not contents.result or not contents.result.lines:
            print("No OCR data available for selected word detection")
            return None
            
        cursor_x, cursor_y = cursor_pos
        candidates = []
        
        # Search all words for candidates to the RIGHT of cursor
        for line_idx, line in enumerate(contents.result.lines):
            for word_idx, word in enumerate(line.words):
                # Calculate word coordinates: LEFT EDGE for selected word (not center!)
                word_left_x = word.left
                word_center_y = word.top + word.height // 2
                
                # Word must be to the RIGHT of cursor (x-coordinate higher)
                if word_left_x > cursor_x:
                    # And within reasonable vertical proximity (50px tolerance)
                    vertical_distance = abs(word_center_y - cursor_y)
                    if vertical_distance <= 50:
                        # Filter out likely OCR fragments (single characters, short words)
                        is_likely_fragment = len(word.text.strip()) <= 1
                        
                        candidates.append({
                            'text': word.text,
                            'coords': (word_left_x, word_center_y),  # LEFT EDGE, not center
                            'distance_from_cursor': word_left_x - cursor_x,
                            'vertical_distance': vertical_distance,
                            'is_above_cursor': word_center_y < cursor_y,
                            'is_likely_fragment': is_likely_fragment,
                            'word_length': len(word.text.strip())
                        })
        
        if not candidates:
            print(f"No words found to the right of cursor at {cursor_pos}")
            return None
        
        # Advanced selection logic prioritizing proper menu items
        # 1. Filter out obvious fragments if we have better options
        non_fragments = [c for c in candidates if not c['is_likely_fragment']]
        if non_fragments:
            candidates = non_fragments
            print(f"Filtered out {len([c for c in candidates if c['is_likely_fragment']])} single-character candidates")
        
        # 2. Filter out words that are too far horizontally (likely from different menu sections)
        horizontal_threshold = 150  # Maximum horizontal distance in pixels
        nearby_candidates = [c for c in candidates if c['distance_from_cursor'] <= horizontal_threshold]
        if nearby_candidates:
            candidates = nearby_candidates
            filtered_count = len([c for c in candidates if c['distance_from_cursor'] > horizontal_threshold])
            print(f"Filtered out {filtered_count} candidates beyond {horizontal_threshold}px horizontal distance")
        
        # 3. Prioritize words ABOVE cursor (typical menu item position)
        words_above = [c for c in candidates if c['is_above_cursor']]
        if words_above:
            candidates = words_above
            print(f"Prioritizing {len(words_above)} words above cursor position")
        
        # 4. Sort by vertical proximity first (closer to cursor Y), then horizontal distance
        selected_word = min(candidates, key=lambda w: (w['vertical_distance'], w['distance_from_cursor']))
        
        # Debug logging to show selection process
        print(f"=== SELECTED WORD DETECTION RESULTS ===")
        print(f"Cursor position: {cursor_pos}")
        print(f"Final candidates after filtering:")
        for i, candidate in enumerate(sorted(candidates, key=lambda w: (w['vertical_distance'], w['distance_from_cursor']))):
            marker = "← SELECTED" if candidate == selected_word else ""
            print(f"  {i+1}. '{candidate['text']}' at {candidate['coords']} "
                  f"(vert_dist: {candidate['vertical_distance']:.1f}, "
                  f"horiz_dist: {candidate['distance_from_cursor']:.1f}, "
                  f"above: {candidate['is_above_cursor']}) {marker}")
        print(f"SELECTED: '{selected_word['text']}' at {selected_word['coords']}")
        
        return selected_word
        
    except Exception as e:
        print(f"Error in find_currently_selected_word: {e}")
        return None

@mod.action_class
class CoreNavigationActions:
    def navigate_step(target_text: str, highlight_image: str, use_wasd: bool, max_steps: int = None, extra_step: bool = False, action_button: str = None, action_count: int = 1, action_interval: float = 0.1) -> bool:
        """Single navigation step - check proximity and move if needed"""
        global navigation_steps_taken, last_direction_pressed, cursor_position_history
        
        # Check navigation mode - use grid navigation if enabled
        navigation_mode = settings.get("user.navigation_mode")
        if navigation_mode == "grid":
            return actions.user.navigate_step_grid(target_text, highlight_image, use_wasd, max_steps, action_button, action_count, action_interval)
        
        # No step limits for main navigation
            
        try:
            # Get current coordinates
            text_coords = actions.user.get_text_coordinates(target_text)
            if not text_coords:
                print(f"Could not find text: {target_text}")
                actions.user.stop_continuous_navigation()
                return False

            # Try flexible cursor detection first (game-specific cursors), fall back to standard method
            highlight_center = actions.user.find_cursor_flexible()
            if not highlight_center:
                # Fallback to original method
                images_to_click_location = "/Users/jarrod/.talon/user/jarrod/gaming/images_to_click/"
                highlight_coords = actions.user.mouse_helper_find_template_relative(
                    f"{images_to_click_location}{highlight_image}"
                )
                if not highlight_coords:
                    print(f"Could not find highlight image: {highlight_image} - stopping navigation")
                    actions.user.stop_continuous_navigation()
                    return False
                
                print(f"Found {len(highlight_coords)} highlight matches using standard method")
                highlight_rect = highlight_coords[0]
                highlight_center = (highlight_rect.x + highlight_rect.width//2, highlight_rect.y + highlight_rect.height//2)
            else:
                print(f"Found highlight using flexible template matching")
            
            # Loop detection - check if we've been here before
            cursor_position_history.append(highlight_center)
            if len(cursor_position_history) > 12:  # Keep last 12 positions for better pattern detection
                cursor_position_history.pop(0)
            
            # Track stable positions for better tiebreaker logic
            actions.user.add_position_if_stable(highlight_center)
                
            # Enhanced loop detection with tiebreaker mode - detect repeating patterns of any length
            if len(cursor_position_history) >= 4:
                # Robust pattern detection: find any repeating sequence of positions
                pattern_detected, detected_pattern = actions.user.detect_repeating_pattern(cursor_position_history)
                
                if pattern_detected:
                    print(f"TIEBREAKER MODE: Repeating pattern detected!")
                    print(f"Pattern: {' -> '.join([f'({p[0]:.0f},{p[1]:.0f})' for p in detected_pattern])}")
                    print(f"Finding closest stable position to target...")
                    
                    # Find closest stable position from history to target
                    closest_position = actions.user.find_closest_stable_position_to_target(text_coords)
                    
                    # Fallback to regular position history if no stable positions yet
                    if not closest_position:
                        print("No stable positions available, falling back to regular position history")
                        closest_position = actions.user.find_closest_position_to_target(cursor_position_history, text_coords)
                    
                    if closest_position:
                        # Check if we're already at the closest position
                        distance_to_closest = actions.user.calculate_distance(highlight_center, closest_position)
                        
                        if distance_to_closest <= 30:  # Within 30px of closest position
                            print(f"TIEBREAKER SUCCESS: At closest reachable position to target!")
                            print(f"Current: {highlight_center}, Closest position: {closest_position}, Target: {text_coords}")
                            if action_button:
                                print(f"Pressing action button: {action_button}")
                                press_action_button_multiple(action_button, action_count, action_interval)
                            actions.user.stop_continuous_navigation()
                            return True
                        else:
                            print(f"Navigating to closest position: {closest_position}")
                            # Navigate toward the closest position instead of original target
                            text_coords = closest_position  # Override target for this step
                            # Override navigation mode to unified for tiebreaker
                            navigation_mode = "unified"
                            print(f"TIEBREAKER: Overriding navigation mode to 'unified' to reach closest position")
                    else:
                        print(f"No position history found, stopping navigation")
                        actions.user.stop_continuous_navigation()
                        return False
            
            # NEW: Find currently selected word for direction calculation
            selected_word = find_currently_selected_word(highlight_center)
            navigation_source = highlight_center  # Default fallback to cursor position
            
            if selected_word:
                # Use selected word coordinates for direction calculation
                navigation_source = selected_word['coords']
                print(f"=== WORD-TO-WORD NAVIGATION ===")
                print(f"Selected word: '{selected_word['text']}' at {navigation_source}")
                print(f"Target word: '{target_text}' at {text_coords}")
            else:
                # Fallback to cursor-based navigation
                print(f"=== CURSOR-BASED NAVIGATION (fallback) ===")
                print(f"Cursor coords: {highlight_center}")
                print(f"Target '{target_text}' coords: {text_coords}")
            
            # Calculate direction using selected word (or cursor fallback) → target
            x_diff = text_coords[0] - navigation_source[0]
            y_diff = text_coords[1] - navigation_source[1]
            
            # But use cursor position for proximity detection (arrival check)
            cursor_x_diff = text_coords[0] - highlight_center[0]
            cursor_y_diff = text_coords[1] - highlight_center[1]
            
            # Get configurable proximity settings
            proximity_x = settings.get("user.highlight_proximity_x")
            proximity_y = settings.get("user.highlight_proximity_y")
            
            print(f"Direction calculation - X diff: {x_diff:.1f}, Y diff: {y_diff:.1f}")
            print(f"Proximity check (cursor) - X diff: {cursor_x_diff:.1f}, Y diff: {cursor_y_diff:.1f}")
            print(f"Mode: {navigation_mode}")
            
            if navigation_mode == "vertical":
                # Vertical mode - Y check only (use cursor position for proximity)
                is_on_target = abs(cursor_y_diff) <= proximity_y
                print(f"Vertical mode - Y close: {abs(cursor_y_diff)} <= {proximity_y}, On target: {is_on_target}")
            elif navigation_mode == "horizontal":
                # Horizontal mode - X check only (use cursor position for proximity)
                is_on_target = abs(cursor_x_diff) <= proximity_x
                print(f"Horizontal mode - X close: {abs(cursor_x_diff)} <= {proximity_x}, On target: {is_on_target}")
            else:
                # Unified mode - use configurable X/Y proximity (use cursor position for proximity)
                is_on_target = abs(cursor_x_diff) <= proximity_x and abs(cursor_y_diff) <= proximity_y
                print(f"Unified mode - X close: {abs(cursor_x_diff)} <= {proximity_x}, Y close: {abs(cursor_y_diff)} <= {proximity_y}, On target: {is_on_target}")
            
            if is_on_target:
                if action_button:
                    print(f"Reached target! Pressing action button: {action_button}")
                    press_action_button_multiple(action_button, action_count, action_interval)
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

            # Calculate direction and move
            print(f"Continuing navigation - X diff: {x_diff:.1f}, Y diff: {y_diff:.1f}")
            
            if navigation_mode == "vertical":
                # Vertical mode - prioritize vertical movement
                if abs(y_diff) > 10:
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
                else:
                    # Move horizontally when vertically aligned
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
            elif navigation_mode == "horizontal":
                # Horizontal mode - prioritize horizontal movement
                if abs(x_diff) > proximity_x:
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
                    # Move vertically when horizontally aligned
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

    def start_continuous_navigation(target_text: str, highlight_image: str, use_wasd: bool = False, max_steps: int = None, extra_step: bool = False, action_button: str = None, action_count: int = 1, action_interval: float = 0.1) -> None:
        """Start continuous navigation with cron job until target reached or game_stop called"""
        global navigation_job, navigation_steps_taken, last_direction_pressed, cursor_position_history
        
        # Stop any existing navigation
        if navigation_job:
            cron.cancel(navigation_job)
            navigation_job = None
        
        # Reset navigation state
        navigation_steps_taken = 0
        last_direction_pressed = None
        cursor_position_history = []
        
        # Clear pattern detection tracking
        actions.user.clear_position_tracking()
        
        navigation_interval = settings.get("user.navigation_interval")
        
        def safe_navigate_step():
            try:
                return actions.user.navigate_step(target_text, highlight_image, use_wasd, max_steps, extra_step, action_button, action_count, action_interval)
            except Exception as e:
                print(f"Navigation step error (continuing): {str(e)}")
                return False  # Continue navigation despite errors
        
        navigation_job = cron.interval(f"{navigation_interval}ms", safe_navigate_step)
        max_steps_text = f" (max {max_steps} steps)" if max_steps else ""
        action_text = f" (will press '{action_button}')" if action_button else ""
        print(f"Started continuous navigation to '{target_text}'{action_text} every {navigation_interval}ms{max_steps_text}")

    def stop_continuous_navigation() -> None:
        """Stop the continuous navigation job"""
        global navigation_job
        if navigation_job:
            cron.cancel(navigation_job)
            navigation_job = None
            print("Stopped continuous navigation")

    def navigate_continuously(target_text: str, highlight_image: str, use_wasd: bool = True, max_steps: int = None, extra_step: bool = False, action_button: str = None, action_count: int = 1, action_interval: float = 0.1) -> None:
        """Start continuous navigation with configurable input method and behavior"""
        actions.user.start_continuous_navigation(target_text, highlight_image, use_wasd, max_steps, extra_step, action_button, action_count, action_interval)

    # Backwards compatibility wrappers
    def navigate_continuously_wasd(target_text: str, highlight_image: str, action_button: str = None) -> None:
        """Start continuous navigation using WASD keys"""
        actions.user.navigate_continuously(target_text, highlight_image, True, None, False, action_button, 1, 0.1)

    def navigate_continuously_arrows(target_text: str, highlight_image: str, action_button: str = None) -> None:
        """Start continuous navigation using arrow keys"""
        actions.user.navigate_continuously(target_text, highlight_image, False, None, False, action_button, 1, 0.1)

    def navigate_continuously_wasd_extra(target_text: str, highlight_image: str, max_steps: int = None, action_button: str = None) -> None:
        """Start continuous navigation using WASD keys with extra step"""
        actions.user.navigate_continuously(target_text, highlight_image, True, max_steps, True, action_button, 1, 0.1)

    def navigate_continuously_arrows_extra(target_text: str, highlight_image: str, action_button: str = None) -> None:
        """Start continuous navigation using arrow keys with extra step"""
        actions.user.navigate_continuously(target_text, highlight_image, False, None, True, action_button, 1, 0.1)

    def navigate_to_word(word: str, use_wasd: bool = None, max_steps: int = None, action_button: str = None, use_configured_action: bool = False, action_count: int = 1, action_interval: float = 0.1) -> None:
        """Navigate to any word found via OCR with configurable input method and action"""
        # Always use configured highlight image from settings
        highlight_image = settings.get("user.highlight_image")
        
        # Determine input method
        if use_wasd is None:
            use_wasd = settings.get("user.uses_wasd")
        
        # Convert word to proper case for search - handle TimestampedText objects
        if hasattr(word, 'text'):
            target_text = word.text.capitalize()
        else:
            target_text = str(word).capitalize()
        
        # Use configured action button if requested
        if use_configured_action:
            action_button = settings.get("user.game_action_button")
        
        # Print appropriate message
        if action_button:
            print(f"Navigating to word: '{target_text}' and selecting with '{action_button}'")
        else:
            print(f"Navigating to word: '{target_text}' using configurable navigation system")
            
        actions.user.start_continuous_navigation(target_text, highlight_image, use_wasd, max_steps, False, action_button, action_count, action_interval)

    def navigate_to_word_with_action(word: object):
        """Navigate to word using configured input method and press configured action button"""
        actions.user.navigate_to_word(word, None, None, None, True)

    # Backwards compatibility wrappers
    def navigate_to_word_wasd(word: str, max_steps: int = None, action_button: str = None, action_count: int = 1, action_interval: float = 0.1) -> None:
        """Navigate to any word found via OCR using WASD, optionally pressing action button when reached"""
        actions.user.navigate_to_word(word, True, max_steps, action_button, False, action_count, action_interval)

    def navigate_to_word_wasd_with_action(word: str) -> None:
        """Navigate to any word found via OCR using WASD and press the configured action button"""
        actions.user.navigate_to_word(word, True, None, None, True)