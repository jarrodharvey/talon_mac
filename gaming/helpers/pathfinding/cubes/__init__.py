"""
Cube-based UI navigation system.

Provides visual grid overlays with numbered cubes for navigating to non-text UI elements.
"""

from talon import Module, actions, settings, canvas, ui, cron
from talon.types import Rect as TalonRect
from talon.skia import Paint
import sys
import io
import json
import re
from contextlib import redirect_stdout

mod = Module()

# Global variables for cube functionality
cube_rectangles = []  # Store detected UI rectangles for cube navigation
cube_canvas = None  # Canvas for cube overlay
cube_showing = False  # Track cube visibility state

# Simple class wrapper for cube drawing (needed for canvas registration)
class CubeDrawer:
    def draw(self, canvas_obj):
        """Draw numbered cubes on canvas overlay using user settings"""
        global cube_rectangles
        
        print(f"CubeDrawer.draw() called with {len(cube_rectangles)} rectangles")
        
        if not cube_rectangles:
            print("No cube_rectangles to draw")
            return
            
        try:
            # Get colors and settings from user configuration
            cube_bg_color = settings.get("user.cube_background_color")
            cube_stroke_color = settings.get("user.cube_stroke_color") 
            cube_text_color = settings.get("user.cube_text_color")
            cube_text_bg_color = settings.get("user.cube_text_background_color")
            cube_transparency = int(settings.get("user.cube_transparency"), 16)
            cube_text_transparency = int(settings.get("user.cube_text_transparency"), 16)
            stroke_width = settings.get("user.cube_stroke_width")
            text_size = settings.get("user.cube_text_size")
            font_family = settings.get("user.cube_font")
            
            # Set up paint for cube boxes
            canvas_obj.paint.color = f"{cube_stroke_color}{cube_transparency:02X}"
            canvas_obj.paint.style = Paint.Style.STROKE
            canvas_obj.paint.stroke_width = stroke_width
            canvas_obj.paint.typeface = font_family
            
            # Draw cube rectangles and numbers
            for index, rect in enumerate(cube_rectangles):
                # Draw rectangle border
                canvas_obj.draw_rect(rect)
                
                # Set up text for cube numbers
                canvas_obj.paint.style = Paint.Style.FILL
                canvas_obj.paint.color = f"{cube_text_bg_color}{cube_text_transparency:02X}"
                canvas_obj.paint.text_align = canvas_obj.paint.TextAlign.LEFT
                canvas_obj.paint.textsize = text_size
                
                # Calculate text position (top-left corner)
                cube_label = str(index)
                text_rect = canvas_obj.paint.measure_text(cube_label)[1]
                background_rect = text_rect.copy()
                background_rect.x = rect.x + 2
                background_rect.y = rect.y + 2
                background_rect.width = text_rect.width + 4
                background_rect.height = text_rect.height + 4
                
                # Draw text background
                canvas_obj.draw_rect(background_rect)
                
                # Draw cube number text
                canvas_obj.paint.color = f"{cube_text_color}{cube_text_transparency:02X}"
                canvas_obj.draw_text(
                    cube_label,
                    rect.x + 4,
                    rect.y + text_rect.height + 2
                )
                
                # Reset for next rectangle
                canvas_obj.paint.color = f"{cube_stroke_color}{cube_transparency:02X}"
                canvas_obj.paint.style = Paint.Style.STROKE
                
        except Exception as e:
            print(f"Error drawing cubes: {e}")

# Global cube drawer instance
cube_drawer = CubeDrawer()

@mod.action_class
class CubeActions:
    def show_cubes() -> None:
        """Use flex-mouse-grid's box detection to find UI rectangles and display them as light blue numbered cubes"""
        global cube_rectangles, cube_canvas, cube_showing
        
        try:
            print("=== DETECTING UI CUBES ===")
            
            # Access the flex-mouse-grid controller 
            flex_grid_controller = None
            for module_name, module in sys.modules.items():
                if 'flex_mouse_grid' in module_name and hasattr(module, 'mg'):
                    flex_grid_controller = module.mg
                    break
            
            if not flex_grid_controller:
                print("ERROR: Could not find flex-mouse-grid controller")
                return
            
            # Hide any existing overlays first
            flex_grid_controller.toggle_boxes(False)
            
            # Try to call the box detection algorithm directly without visual display
            try:
                # Try different detection parameters to find character portraits
                # Current issue: all detection in bottom area (Y 1361-1811), portraits in upper area (Y 150-400)
                threshold = 50   # Much higher threshold to focus on high-contrast UI elements
                lower = 80       # Larger minimum size for character portraits
                upper = 120      # Tighter size range for portraits
                
                print(f"Running HIGH-CONTRAST detection with threshold={threshold}, lower={lower}, upper={upper}")
                
                # Call the detection method directly (this should not show visual overlay)
                flex_grid_controller.find_boxes_with_config(threshold, lower, upper)
                
            except Exception as e:
                print(f"Direct detection failed: {e}, falling back to standard method")
                # Fallback to the normal method
                actions.user.flex_grid_find_boxes()
                # Immediately hide the overlay
                flex_grid_controller.toggle_boxes(False)
            
            # Get detected boxes from flex-mouse-grid 
            detected_boxes = flex_grid_controller.boxes
            if not detected_boxes:
                print("No UI rectangles detected")
                return
                
            print(f"Found {len(detected_boxes)} UI rectangles")
            
            # Filter for character portrait dimensions specifically
            # Based on screenshot analysis, portraits are roughly 90x80 pixels
            min_width = 70   # Character portraits are substantial UI elements
            min_height = 60  # Character portraits have significant height  
            max_count = 10   # Very few, highly targeted cubes
            
            # Since we can see the raw JSON coordinates being printed to logs,
            # let's try to capture and parse that data directly
            
            # Parse the most recent JSON output from the logs
            # The JSON data shows the correct screen coordinates we need
            filtered_boxes = []
            
            # Try to get the raw coordinates by re-running the detection with capturing
            # Capture the JSON output from flex_grid_find_boxes
            captured_output = io.StringIO()
            try:
                with redirect_stdout(captured_output):
                    # Re-run box detection to capture the JSON output
                    actions.user.flex_grid_find_boxes()
                    # Immediately hide any visual overlays
                    flex_grid_controller.toggle_boxes(False)
                    
                output_text = captured_output.getvalue()
                
                # Look for JSON in the captured output
                json_match = re.search(r'\{"boxes":\[.*?\],"threshold":\d+\}', output_text)
                
                if json_match:
                    json_data = json.loads(json_match.group())
                    raw_boxes = json_data.get("boxes", [])
                    print(f"Successfully parsed {len(raw_boxes)} boxes from JSON output")
                    
                    # Filter and create TalonRect objects with proper coordinates
                    for raw_box in raw_boxes:
                        if raw_box["w"] >= min_width and raw_box["h"] >= min_height:
                            rect = TalonRect(raw_box["x"], raw_box["y"], raw_box["w"], raw_box["h"])
                            filtered_boxes.append(rect)
                            if len(filtered_boxes) >= max_count:
                                break
                else:
                    print("Could not find JSON data in output, using fallback")
                    # Fallback to detected_boxes
                    for box in detected_boxes:
                        if box.width >= min_width and box.height >= min_height:
                            filtered_boxes.append(box)
                            if len(filtered_boxes) >= max_count:
                                break
                                
            except Exception as e:
                print(f"Error capturing JSON output: {e}")
                # Final fallback
                for box in detected_boxes:
                    if box.width >= min_width and box.height >= min_height:
                        filtered_boxes.append(box)
                        if len(filtered_boxes) >= max_count:
                            break
            
            print(f"Filtered to {len(filtered_boxes)} cubes (min size: {min_width}x{min_height}, max count: {max_count})")
            
            # Debug: Print ALL detected rectangles to understand what we're getting
            print("=== ALL DETECTED RECTANGLES ===")
            for i, box in enumerate(filtered_boxes[:10]):  # Show first 10
                print(f"Box {i}: x={box.x}, y={box.y}, w={box.width}, h={box.height}")
            if len(filtered_boxes) > 10:
                print(f"... and {len(filtered_boxes) - 10} more rectangles")
            
            # Debug coordinate ranges and distribution
            if filtered_boxes:
                all_x = [box.x for box in filtered_boxes]
                all_y = [box.y for box in filtered_boxes] 
                print(f"Coordinate ranges - X: {min(all_x)} to {max(all_x)}, Y: {min(all_y)} to {max(all_y)}")
                
                main_screen = ui.main_screen()
                screen_width, screen_height = main_screen.width, main_screen.height
                print(f"Screen size: {screen_width} x {screen_height}")
                print(f"Screen rect: {main_screen.rect}")
                
                # Check if rectangles are clustered in certain areas
                bottom_third = screen_height * 2 / 3
                bottom_count = sum(1 for box in filtered_boxes if box.y > bottom_third)
                print(f"Rectangles in bottom third of screen: {bottom_count}/{len(filtered_boxes)}")
                
                # Check for very small rectangles that might be artifacts
                tiny_count = sum(1 for box in filtered_boxes if box.width < 10 or box.height < 10)
                print(f"Tiny rectangles (< 10px width/height): {tiny_count}/{len(filtered_boxes)}")
                
                # Check rectangle sizes distribution
                sizes = [(box.width, box.height) for box in filtered_boxes[:5]]
                print(f"Rectangle sizes (first 5): {sizes}")
                
                # Analysis: Are we detecting in the right area?
                portrait_area_y = screen_height * 0.5  # Character portraits should be in upper half
                upper_count = sum(1 for box in filtered_boxes if box.y < portrait_area_y)
                print(f"Rectangles in upper half (where portraits should be): {upper_count}/{len(filtered_boxes)}")
                
                if upper_count == 0:
                    print("WARNING: No rectangles detected in portrait area - detection algorithm may need different settings")
                print(f"Screen rect: {main_screen.rect}")
            
            # Store rectangles for navigation
            cube_rectangles = filtered_boxes
            
            # Hide flex-mouse-grid's default overlay (we'll show our own)
            flex_grid_controller.toggle_boxes(False)
            
            # Create our own canvas overlay with light blue cubes
            screen = ui.main_screen()
            print(f"Creating canvas on screen: {screen}")
            print(f"Screen dimensions: {screen.width} x {screen.height}")
            print(f"Screen rect: {screen.rect}")
            
            # Get flex-mouse-grid's detection area for coordinate transformation
            detection_rect = flex_grid_controller.rect
            print(f"Flex-mouse-grid detection area: {detection_rect}")
            print(f"Canvas screen area: {screen.rect}")
            
            # Apply coordinate transformation if detection area differs from canvas screen
            transformed_rectangles = []
            if detection_rect.x != screen.rect.x or detection_rect.y != screen.rect.y or detection_rect.width != screen.rect.width or detection_rect.height != screen.rect.height:
                print("Applying coordinate transformation from detection area to canvas screen")
                print(f"Before transformation - sample box: x={cube_rectangles[0].x}, y={cube_rectangles[0].y}")
                print(f"Detection offset: ({detection_rect.x}, {detection_rect.y})")
                print(f"Canvas offset: ({screen.rect.x}, {screen.rect.y})")
                
                # Check if we need to scale coordinates (multi-monitor situation)
                max_detected_x = max(rect.x + rect.width for rect in cube_rectangles)
                max_detected_y = max(rect.y + rect.height for rect in cube_rectangles)
                
                print(f"Max detected coordinates: ({max_detected_x}, {max_detected_y})")
                print(f"Detection area size: ({detection_rect.width}, {detection_rect.height})")
                
                needs_scaling = max_detected_x > detection_rect.width or max_detected_y > detection_rect.height
                
                if needs_scaling:
                    # Scale coordinates from full desktop to canvas screen
                    scale_x = screen.width / max_detected_x if max_detected_x > screen.width else 1.0
                    scale_y = screen.height / max_detected_y if max_detected_y > screen.height else 1.0
                    print(f"Applying coordinate scaling: x={scale_x:.3f}, y={scale_y:.3f}")
                else:
                    scale_x = scale_y = 1.0
                    print("Using simple offset transformation")
                
                for i, rect in enumerate(cube_rectangles):
                    # Transform from detection coordinates to canvas coordinates
                    original_x, original_y = rect.x, rect.y
                    
                    if needs_scaling:
                        # Scale first, then offset
                        transformed_x = rect.x * scale_x
                        transformed_y = rect.y * scale_y
                    else:
                        # Simple offset transformation
                        transformed_x = rect.x - detection_rect.x + screen.rect.x
                        transformed_y = rect.y - detection_rect.y + screen.rect.y
                    
                    if i == 0:  # Debug first box transformation
                        print(f"Box 0 transformation: ({original_x}, {original_y}) -> ({transformed_x:.1f}, {transformed_y:.1f})")
                    
                    # Create new rectangle with transformed coordinates
                    from talon.types import Rect
                    transformed_rect = Rect(transformed_x, transformed_y, rect.width * scale_x, rect.height * scale_y)
                    transformed_rectangles.append(transformed_rect)
                    
                cube_rectangles = transformed_rectangles
                print(f"Transformed {len(cube_rectangles)} rectangles to canvas coordinate space")
                if cube_rectangles:
                    first_box = cube_rectangles[0]
                    print(f"First transformed box: x={first_box.x}, y={first_box.y}")
                    # Check if still out of bounds
                    if first_box.x >= screen.width or first_box.y >= screen.height:
                        print(f"ERROR: Transformed coordinates still out of bounds! Canvas size: {screen.width}x{screen.height}")
            else:
                print("No coordinate transformation needed - detection and canvas areas match")
            
            if cube_canvas:
                print("Closing existing cube_canvas")
                cube_canvas.close()
                
            print("Creating new canvas from screen")
            cube_canvas = canvas.Canvas.from_screen(screen)
            
            print("Registering draw function")
            cube_canvas.register("draw", cube_drawer.draw)
            
            cube_showing = True
            
            print("Freezing canvas to display")
            cube_canvas.freeze()
            
            print(f"Canvas created and frozen - should be showing {len(cube_rectangles)} cubes")
            
        except Exception as e:
            print(f"Error showing cubes: {e}")
            actions.user.hide_cubes()

    def navigate_to_cube(number: int) -> None:
        """Navigate the game cursor to the left edge of the specified cube using continuous navigation"""
        global cube_rectangles
        
        try:
            if not cube_rectangles:
                print("No cubes detected. Run 'show cubes' first.")
                return
                
            if number < 0 or number >= len(cube_rectangles):
                print(f"Invalid cube number: {number}. Available cubes: 0-{len(cube_rectangles)-1}")
                return
                
            target_rect = cube_rectangles[number]
            
            # Calculate target coordinates using offset setting
            target_offset_x = settings.get("user.cube_target_offset_x")
            target_x = target_rect.x + target_offset_x
            target_y = target_rect.y + target_rect.height // 2  # Vertical center
            
            print(f"Starting continuous navigation to cube {number} at left edge: ({target_x}, {target_y})")
            
            # Use existing continuous navigation system by creating a fake "cube target"
            # We'll temporarily store the target coordinates and use cube-specific navigation
            actions.user.start_cube_navigation(number, target_x, target_y)
                    
        except Exception as e:
            print(f"Error navigating to cube {number}: {e}")

    def start_cube_navigation(number: int, target_x: float, target_y: float) -> None:
        """Start continuous navigation to cube target coordinates"""
        # Import global variables from navigation module
        from ..core.navigation import navigation_job, navigation_steps_taken, last_direction_pressed, cursor_position_history
        
        # Stop any existing navigation
        actions.user.stop_continuous_navigation()
        
        # Reset step counter, direction tracking, and position history
        # These will be managed by the cube_navigate_step function
        
        # Clear pattern detection tracking
        actions.user.clear_position_tracking()
        
        # Start new navigation job with cube-specific logic
        navigation_interval = settings.get("user.navigation_interval")
        
        def safe_cube_navigate_step():
            try:
                return actions.user.cube_navigate_step(number, target_x, target_y)
            except Exception as e:
                print(f"Cube navigation step error (continuing): {str(e)}")
                return False  # Continue navigation despite errors
        
        # Use the global navigation_job variable from navigation module
        from ..core import navigation
        navigation.navigation_job = cron.interval(f"{navigation_interval}ms", safe_cube_navigate_step)
        print(f"Started continuous cube navigation to cube {number} every {navigation_interval}ms")

    def cube_navigate_step(number: int, target_x: float, target_y: float) -> bool:
        """Single navigation step toward cube target - returns True if reached"""
        # Import global variables from navigation module  
        from ..core.navigation import navigation_steps_taken, last_direction_pressed, cursor_position_history
        
        try:
            target_coords = (target_x, target_y)
            
            # Try flexible cursor detection
            cursor_pos = actions.user.find_cursor_flexible()
            if not cursor_pos:
                print("Could not detect cursor position")
                actions.user.stop_continuous_navigation()
                return False
            
            # Loop detection - check if we've been here before
            cursor_position_history.append(cursor_pos)
            if len(cursor_position_history) > 12:  # Keep last 12 positions for better pattern detection
                cursor_position_history.pop(0)
            
            # Track stable positions for better tiebreaker logic
            actions.user.add_position_if_stable(cursor_pos)
                
            # Enhanced loop detection with tiebreaker mode - detect repeating patterns of any length
            if len(cursor_position_history) >= 4:
                # Robust pattern detection: find any repeating sequence of positions
                pattern_detected, detected_pattern = actions.user.detect_repeating_pattern(cursor_position_history)
                
                if pattern_detected:
                    print(f"CUBE TIEBREAKER MODE: Repeating pattern detected!")
                    print(f"Pattern: {' -> '.join([f'({p[0]:.0f},{p[1]:.0f})' for p in detected_pattern])}")
                    print(f"Finding closest stable position to cube {number}...")
                    
                    # Find closest stable position from history to target
                    closest_position = actions.user.find_closest_stable_position_to_target(target_coords)
                    
                    # Fallback to regular position history if no stable positions yet
                    if not closest_position:
                        print("No stable positions available, falling back to regular position history")
                        closest_position = actions.user.find_closest_position_to_target(cursor_position_history, target_coords)
                    
                    if closest_position:
                        # Check if we're already at the closest position
                        distance_to_closest = actions.user.calculate_distance(cursor_pos, closest_position)
                        
                        if distance_to_closest <= 30:  # Within 30px of closest position
                            print(f"CUBE TIEBREAKER SUCCESS: At closest reachable position to cube {number}!")
                            print(f"Current: {cursor_pos}, Closest position: {closest_position}, Target: {target_coords}")
                            actions.user.stop_continuous_navigation()
                            return True
            
            # Calculate direction differences
            x_diff = target_coords[0] - cursor_pos[0]
            y_diff = target_coords[1] - cursor_pos[1]
            
            print(f"=== CUBE NAVIGATION STEP ===")
            print(f"Cube {number} target: {target_coords}")
            print(f"Cursor: {cursor_pos}")
            print(f"X diff: {x_diff:.1f} (positive = target is RIGHT)")
            print(f"Y diff: {y_diff:.1f} (positive = target is DOWN)")
            
            # Check proximity using configurable settings
            proximity_x = settings.get("user.highlight_proximity_x")
            proximity_y = settings.get("user.highlight_proximity_y")
            
            # Check if we've reached the target
            if abs(x_diff) <= proximity_x and abs(y_diff) <= proximity_y:
                print(f"Reached cube {number}! Target: {target_coords}, Cursor: {cursor_pos}")
                print(f"Final differences - X: {x_diff:.1f}, Y: {y_diff:.1f}")
                actions.user.stop_continuous_navigation()
                return True

            # Continue navigation - move in direction with larger difference (unified mode)
            use_wasd = settings.get("user.uses_wasd")
            
            if abs(x_diff) > abs(y_diff):
                if x_diff > 0:
                    key_to_press = "d" if use_wasd else "right"
                    print(f"Pressing {key_to_press} (right)")
                    actions.key(key_to_press)
                    # Update global variable
                    from ..core import navigation
                    navigation.last_direction_pressed = key_to_press
                else:
                    key_to_press = "a" if use_wasd else "left"
                    print(f"Pressing {key_to_press} (left)")
                    actions.key(key_to_press)
                    # Update global variable
                    from ..core import navigation
                    navigation.last_direction_pressed = key_to_press
            else:
                if y_diff > 0:
                    key_to_press = "s" if use_wasd else "down"
                    print(f"Pressing {key_to_press} (down)")
                    actions.key(key_to_press)
                    # Update global variable
                    from ..core import navigation
                    navigation.last_direction_pressed = key_to_press
                else:
                    key_to_press = "w" if use_wasd else "up"
                    print(f"Pressing {key_to_press} (up)")
                    actions.key(key_to_press)
                    # Update global variable
                    from ..core import navigation
                    navigation.last_direction_pressed = key_to_press
            
            # Increment step counter
            from ..core import navigation
            navigation.navigation_steps_taken += 1        
            return False  # Continue navigation
            
        except Exception as e:
            print(f"Cube navigation step error: {str(e)}")
            actions.user.stop_continuous_navigation()
            return False

    def hide_cubes() -> None:
        """Hide the cube overlay"""
        global cube_canvas, cube_showing, cube_rectangles
        
        try:
            if cube_canvas:
                cube_canvas.close()
                cube_canvas = None
                
            cube_showing = False
            cube_rectangles = []
            print("Cubes hidden")
            
        except Exception as e:
            print(f"Error hiding cubes: {e}")

    # Cube settings management functions
    def set_cube_background_color(hex_color: str) -> None:
        """Set cube background color"""
        actions.user.settings_set_string("user.cube_background_color", hex_color)
        print(f"Cube background color set to #{hex_color}")

    def set_cube_stroke_color(hex_color: str) -> None:
        """Set cube border color"""
        actions.user.settings_set_string("user.cube_stroke_color", hex_color)
        print(f"Cube border color set to #{hex_color}")

    def set_cube_text_color(hex_color: str) -> None:
        """Set cube text color"""
        actions.user.settings_set_string("user.cube_text_color", hex_color)
        print(f"Cube text color set to #{hex_color}")

    def set_cube_text_background_color(hex_color: str) -> None:
        """Set cube text background color"""
        actions.user.settings_set_string("user.cube_text_background_color", hex_color)
        print(f"Cube text background color set to #{hex_color}")

    def set_cube_transparency(value: int) -> None:
        """Set cube transparency (0-255)"""
        hex_value = f"0x{max(0, min(255, value)):02X}"
        actions.user.settings_set_string("user.cube_transparency", hex_value)
        print(f"Cube transparency set to {hex_value}")

    def set_cube_text_transparency(value: int) -> None:
        """Set cube text transparency (0-255)"""
        hex_value = f"0x{max(0, min(255, value)):02X}"
        actions.user.settings_set_string("user.cube_text_transparency", hex_value)
        print(f"Cube text transparency set to {hex_value}")

    def set_cube_stroke_width(width: int) -> None:
        """Set cube border width"""
        actions.user.settings_set_int("user.cube_stroke_width", max(1, width))
        print(f"Cube border width set to {width}")

    def set_cube_text_size(size: int) -> None:
        """Set cube text size"""
        actions.user.settings_set_int("user.cube_text_size", max(8, size))
        print(f"Cube text size set to {size}")

    def set_cube_font(font_family: str) -> None:
        """Set cube font family"""
        actions.user.settings_set_string("user.cube_font", font_family)
        print(f"Cube font set to {font_family}")

    def set_cube_min_width(width: int) -> None:
        """Set minimum cube width filter"""
        actions.user.settings_set_int("user.cube_min_width", max(1, width))
        print(f"Cube minimum width set to {width}")

    def set_cube_min_height(height: int) -> None:
        """Set minimum cube height filter"""
        actions.user.settings_set_int("user.cube_min_height", max(1, height))
        print(f"Cube minimum height set to {height}")

    def set_cube_max_count(count: int) -> None:
        """Set maximum number of cubes to show"""
        actions.user.settings_set_int("user.cube_max_count", max(1, count))
        print(f"Cube maximum count set to {count}")

    def set_cube_target_offset_x(offset: int) -> None:
        """Set horizontal target offset for cube navigation"""
        actions.user.settings_set_int("user.cube_target_offset_x", max(0, offset))
        print(f"Cube target offset set to {offset}")

    def show_cube_settings() -> None:
        """Display current cube settings"""
        print("=== CUBE SETTINGS ===")
        print(f"Background color: #{settings.get('user.cube_background_color')}")
        print(f"Border color: #{settings.get('user.cube_stroke_color')}")
        print(f"Text color: #{settings.get('user.cube_text_color')}")
        print(f"Text background: #{settings.get('user.cube_text_background_color')}")
        print(f"Transparency: {settings.get('user.cube_transparency')}")
        print(f"Text transparency: {settings.get('user.cube_text_transparency')}")
        print(f"Border width: {settings.get('user.cube_stroke_width')}")
        print(f"Text size: {settings.get('user.cube_text_size')}")
        print(f"Font: {settings.get('user.cube_font')}")
        print(f"Min width: {settings.get('user.cube_min_width')}")
        print(f"Min height: {settings.get('user.cube_min_height')}")
        print(f"Max count: {settings.get('user.cube_max_count')}")
        print(f"Target offset X: {settings.get('user.cube_target_offset_x')}")

    def reset_cube_settings() -> None:
        """Reset all cube settings to defaults"""
        defaults = {
            "user.cube_background_color": "87CEEB",
            "user.cube_stroke_color": "4682B4",
            "user.cube_text_color": "000000",
            "user.cube_text_background_color": "FFFFFF",
            "user.cube_transparency": "0x55",
            "user.cube_text_transparency": "0xCC",
            "user.cube_stroke_width": 2,
            "user.cube_text_size": 16,
            "user.cube_font": "arial",
            "user.cube_min_width": 20,
            "user.cube_min_height": 15,
            "user.cube_max_count": 99,
            "user.cube_target_offset_x": 10
        }
        
        for key, value in defaults.items():
            if isinstance(value, str):
                actions.user.settings_set_string(key, value)
            else:
                actions.user.settings_set_int(key, value)
        
        print("Cube settings reset to defaults")

    def save_cube_settings() -> None:
        """Save current cube settings to game-specific file"""
        print("Cube settings are automatically saved when changed")
        print("Settings persist across Talon restarts")

__all__ = [
    "show_cubes",
    "navigate_to_cube", 
    "hide_cubes",
    "start_cube_navigation",
    "cube_navigate_step",
    "set_cube_background_color",
    "set_cube_stroke_color",
    "set_cube_text_color", 
    "set_cube_text_background_color",
    "set_cube_transparency",
    "set_cube_text_transparency",
    "set_cube_stroke_width",
    "set_cube_text_size",
    "set_cube_font",
    "set_cube_min_width",
    "set_cube_min_height", 
    "set_cube_max_count",
    "set_cube_target_offset_x",
    "show_cube_settings",
    "reset_cube_settings",
    "save_cube_settings"
]