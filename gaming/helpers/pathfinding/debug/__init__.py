"""
Debug tools and testing utilities for pathfinding system.

Provides debug markers, coordinate logging, state inspection, and test functions.
"""

from talon import Module, actions, settings
from talon.types import Rect as TalonRect
import sys
import os

mod = Module()

@mod.action_class
class DebugActions:
    def debug_all_text_coordinates() -> None:
        """Debug function to list all text coordinates found via OCR"""
        print("=== DEBUG: ALL TEXT COORDINATES ===")
        
        # Disconnect eye tracker and scan full screen
        actions.user.disconnect_ocr_eye_tracker()
        
        try:
            # Find OCR controller
            gaze_ocr_controller = None
            for module_name, module in sys.modules.items():
                if 'gaze_ocr' in module_name and hasattr(module, 'gaze_ocr_controller'):
                    gaze_ocr_controller = module.gaze_ocr_controller
                    break
            
            if not gaze_ocr_controller:
                print("ERROR: Could not find gaze_ocr_controller")
                return
                
            # Get OCR scan
            print("Performing OCR scan...")
            gaze_ocr_controller.read_nearby()
            contents = gaze_ocr_controller.latest_screen_contents()
            
            if not contents or not contents.result or not contents.result.lines:
                print("No OCR results found")
                return
                
            print(f"Found {len(contents.result.lines)} lines of text")
            print("Format: 'Text' at (center_x, center_y) [left, top, width, height]")
            print("")
            
            # List all text with coordinates
            for line_idx, line in enumerate(contents.result.lines):
                for word_idx, word in enumerate(line.words):
                    # Calculate center coordinates (same as get_text_coordinates)
                    center_x = word.left + word.width // 2
                    center_y = word.top + word.height // 2
                    
                    print(f"Line {line_idx}, Word {word_idx}: '{word.text}' at ({center_x}, {center_y}) [{word.left}, {word.top}, {word.width}, {word.height}]")
            
            print("=== END DEBUG TEXT COORDINATES ===")
            
        finally:
            # Always reconnect eye tracker
            actions.user.connect_ocr_eye_tracker()

    def debug_cursor_position() -> None:
        """Debug function to show cursor/highlight position using template matching"""
        print("=== DEBUG: CURSOR POSITION ===")
        
        # Get configured highlight image
        highlight_image = settings.get("user.highlight_image")
        images_to_click_location = "/Users/jarrod/.talon/user/jarrod/gaming/images_to_click/"
        image_path = f"{images_to_click_location}{highlight_image}"
        
        print(f"Looking for cursor template: {highlight_image}")
        print(f"Full path: {image_path}")
        
        # Check if image file exists
        if not os.path.exists(image_path):
            print(f"ERROR: Template image not found at {image_path}")
            return
            
        try:
            # Try flexible template matching (same as navigation system)
            flexible_result = actions.user.find_template_flexible(highlight_image)
            
            if flexible_result:
                print(f"Found cursor using flexible template matching:")
                # find_template_flexible returns a single tuple (center_x, center_y)
                center_x, center_y = flexible_result
                print(f"  Flexible match: center ({center_x}, {center_y})")
                print(f"PRIMARY CURSOR (flexible): ({center_x}, {center_y})")
            else:
                print("No cursor matches found with flexible template matching")
                
            # Also try direct template matching for comparison
            print("\nTrying direct mouse_helper_find_template_relative for comparison:")
            direct_matches = actions.user.mouse_helper_find_template_relative(image_path)
            
            if direct_matches:
                print(f"Found {len(direct_matches)} matches with direct template matching:")
                for i, match in enumerate(direct_matches):
                    center_x = match.x + match.width // 2
                    # Use bottom of middle third to prevent false proximity when cursor overlaps target
                    center_y = match.y + 2 * match.height // 3
                    print(f"  Direct match {i}: center ({center_x}, {center_y}) [x={match.x}, y={match.y}, w={match.width}, h={match.height}]")
            else:
                print("No matches found with direct template matching")
                
        except Exception as e:
            print(f"ERROR during template matching: {e}")
            
        print("=== END DEBUG CURSOR POSITION ===")

    def debug_pathfinding_state() -> None:
        """Debug function showing both text coordinates and cursor position for pathfinding analysis"""
        print("=== DEBUG: PATHFINDING STATE ===")
        
        # Get configured highlight image
        highlight_image = settings.get("user.highlight_image")
        images_to_click_location = "/Users/jarrod/.talon/user/jarrod/gaming/images_to_click/"
        image_path = f"{images_to_click_location}{highlight_image}"
        
        print(f"Using cursor template: {highlight_image}")
        
        # First get cursor position - try multiple thresholds
        cursor_coords = None
        try:
            # Test different thresholds and show cursor count
            for threshold in [0.7, 0.8, 0.9]:
                print(f"Testing threshold {threshold}:")
                flexible_result = actions.user.find_template_flexible(highlight_image, [threshold])
                
                # Also test direct template matching to count total matches  
                direct_matches = actions.user.mouse_helper_find_template_relative(image_path)
                if direct_matches:
                    print(f"  Direct matching found {len(direct_matches)} cursor matches at threshold {threshold}")
                    for i, match in enumerate(direct_matches[:5]):  # Show first 5
                        center = (match.x + match.width // 2, match.y + match.height // 2)
                        print(f"    Match {i+1}: {center}")
                else:
                    print(f"  Direct matching found 0 cursor matches at threshold {threshold}")
                    
                if flexible_result:
                    print(f"  Flexible matching selected: {flexible_result}")
                    if not cursor_coords:  # Use first successful match
                        cursor_coords = flexible_result
                        print(f"SELECTED CURSOR POSITION: {cursor_coords} (threshold {threshold})")
                else:
                    print(f"  Flexible matching found: None")
                print("")
                
        except Exception as e:
            print(f"CURSOR POSITION: Error - {e}")
        
        print("")
        
        # Get all text coordinates  
        actions.user.disconnect_ocr_eye_tracker()
        try:
            gaze_ocr_controller = None
            for module_name, module in sys.modules.items():
                if 'gaze_ocr' in module_name and hasattr(module, 'gaze_ocr_controller'):
                    gaze_ocr_controller = module.gaze_ocr_controller
                    break
            
            if not gaze_ocr_controller:
                print("ERROR: Could not find gaze_ocr_controller")
                return
                
            print("Scanning for text...")
            gaze_ocr_controller.read_nearby()
            contents = gaze_ocr_controller.latest_screen_contents()
            
            if not contents or not contents.result or not contents.result.lines:
                print("No text found")
                return
                
            print(f"Found {len(contents.result.lines)} lines of text")
            print("")
            
            # Show all text with distance from cursor if cursor was found
            all_text = []
            for line_idx, line in enumerate(contents.result.lines):
                for word_idx, word in enumerate(line.words):
                    center_x = word.left + word.width // 2
                    center_y = word.top + word.height // 2
                    text_coords = (center_x, center_y)
                    
                    # Calculate distance and direction from cursor if available
                    distance_info = ""
                    direction_info = ""
                    if cursor_coords:
                        x_diff = center_x - cursor_coords[0]  # positive = text is RIGHT of cursor
                        y_diff = center_y - cursor_coords[1]  # positive = text is DOWN from cursor  
                        distance = ((x_diff ** 2) + (y_diff ** 2)) ** 0.5
                        
                        # Direction indicators
                        horizontal = "RIGHT" if x_diff > 0 else "LEFT" if x_diff < 0 else "SAME"
                        vertical = "DOWN" if y_diff > 0 else "UP" if y_diff < 0 else "SAME"
                        
                        distance_info = f" | Distance: {distance:.1f}px"
                        direction_info = f" | Direction: {horizontal}/{vertical} ({x_diff:+.0f},{y_diff:+.0f})"
                    
                    text_entry = {
                        'text': word.text,
                        'coords': text_coords,
                        'distance': distance if cursor_coords else None,
                        'line': line_idx,
                        'word': word_idx
                    }
                    all_text.append(text_entry)
                    
                    print(f"'{word.text}' at {text_coords}{distance_info}{direction_info}")
            
            # If cursor found, show closest text items
            if cursor_coords and all_text:
                print("")
                print("=== CLOSEST TEXT TO CURSOR ===")
                sorted_by_distance = sorted([t for t in all_text if t['distance'] is not None], key=lambda x: x['distance'])
                for i, text_item in enumerate(sorted_by_distance[:5]):  # Show top 5 closest
                    print(f"{i+1}. '{text_item['text']}' at {text_item['coords']} (distance: {text_item['distance']:.1f}px)")
                    
        except Exception as e:
            print(f"ERROR during text scanning: {e}")
        finally:
            actions.user.connect_ocr_eye_tracker()
            
        print("=== END DEBUG PATHFINDING STATE ===")

    def show_pathfinding_debug_markers(target_text: str = "Attack") -> None:
        """Show visual debug markers for cursor and target positions on screen"""
        try:
            print(f"=== SHOWING DEBUG MARKERS FOR '{target_text}' ===")
            
            # Hide any existing markers first to avoid interference
            actions.user.hide_pathfinding_debug_markers()
            
            # Get current cursor position
            highlight_image = settings.get("user.highlight_image")
            print("DEBUG: About to call find_cursor_flexible() from debug markers")
            cursor_pos = actions.user.find_cursor_flexible()
            print(f"DEBUG: find_cursor_flexible() returned: {cursor_pos}")
            if not cursor_pos:
                print("Could not detect cursor position")
                return
            
            # Get target text coordinates
            target_coords = actions.user.get_text_coordinates(target_text)
            if not target_coords:
                print(f"Could not find text: {target_text}")
                return
            
            # NEW: Get currently selected word coordinates
            from ..core.navigation import find_currently_selected_word
            selected_word = find_currently_selected_word(cursor_pos)
            
            print(f"Debug marker - Cursor position: {cursor_pos}")
            if selected_word:
                print(f"Debug marker - Selected word: '{selected_word['text']}' at {selected_word['coords']}")
            else:
                print("Debug marker - Selected word: Not found")
            print(f"Debug marker - Target '{target_text}' position: {target_coords}")
            
            # Create marker rectangles (small 10x10 rectangles around the points)
            marker_size = 10
            marker_rects = []
            
            # Marker A: Cursor position
            cursor_rect = TalonRect(
                cursor_pos[0] - marker_size//2, 
                cursor_pos[1] - marker_size//2, 
                marker_size, 
                marker_size
            )
            marker_rects.append(cursor_rect)
            
            # Marker B: Target position
            target_rect = TalonRect(
                target_coords[0] - marker_size//2, 
                target_coords[1] - marker_size//2, 
                marker_size, 
                marker_size
            )
            marker_rects.append(target_rect)
            
            # Marker C: Selected word position (if found)
            if selected_word:
                selected_word_rect = TalonRect(
                    selected_word['coords'][0] - marker_size//2, 
                    selected_word['coords'][1] - marker_size//2, 
                    marker_size, 
                    marker_size
                )
                marker_rects.append(selected_word_rect)
            
            # Show markers using talon_ui_helper
            actions.user.marker_ui_show(marker_rects)
            
            if selected_word:
                print("Debug markers shown! Marker (a) = Cursor, Marker (b) = Target, Marker (c) = Selected Word")
            else:
                print("Debug markers shown! Marker (a) = Cursor, Marker (b) = Target (Selected word not found)")
            
        except Exception as e:
            print(f"Error showing debug markers: {e}")

    def hide_pathfinding_debug_markers() -> None:
        """Hide visual debug markers"""
        try:
            actions.user.marker_ui_hide()
            print("Debug markers hidden")
        except Exception as e:
            print(f"Error hiding debug markers: {e}")

    def test_continuous_navigation(target_text: str, highlight_image: str, max_steps: int = 3, use_wasd: bool = False, countdown: int = 0) -> None:
        """Test continuous navigation with limited steps for safety"""
        if countdown > 0:
            print(f"Starting navigation to '{target_text}' in {countdown} seconds...")
            actions.sleep(f"{countdown}s")
        actions.user.navigate_continuously(target_text, highlight_image, use_wasd, max_steps)

    def test_grid_analysis() -> None:
        """Test grid structure analysis"""
        grid_info = actions.user.analyze_grid_structure()
        if grid_info.get('columns'):
            print(f"Grid analysis successful: {len(grid_info['columns'])} columns detected")
            for i, column in enumerate(grid_info['columns']):
                print(f"Column {i}: {[item['text'] for item in column]}")
        else:
            print("No grid structure detected")

    def test_grid_navigation(target_text: str, highlight_image: str = None, max_steps: int = 5) -> None:
        """Test grid navigation with safety limits"""
        print(f"Testing grid navigation to '{target_text}' with max {max_steps} steps")
        actions.user.navigate_step_grid(target_text, highlight_image, True, max_steps, None, 1, 0.1)

__all__ = [
    "debug_all_text_coordinates",
    "debug_cursor_position", 
    "debug_pathfinding_state",
    "show_pathfinding_debug_markers",
    "hide_pathfinding_debug_markers",
    "test_continuous_navigation",
    "test_grid_analysis",
    "test_grid_navigation"
]