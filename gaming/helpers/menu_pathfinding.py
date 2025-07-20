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
cursor_position_history = []  # Track cursor positions to detect loops

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
    desc="Navigation mode: 'unified' (X/Y proximity), 'vertical' (prioritize vertical), 'horizontal' (prioritize horizontal), 'grid' (column-first grid navigation)"
)

mod.setting(
    "game_action_button",
    type=str,
    default="space",
    desc="Button to press when selecting/activating menu items after navigation"
)

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

@mod.action_class
class MenuPathfindingActions:
    def analyze_grid_structure() -> dict:
        """Analyze OCR text to detect grid structure (columns/rows)"""
        try:
            # Disconnect eye tracker and get OCR data
            actions.user.disconnect_ocr_eye_tracker()
            
            import sys
            gaze_ocr_controller = None
            for module_name, module in sys.modules.items():
                if 'gaze_ocr' in module_name and hasattr(module, 'gaze_ocr_controller'):
                    gaze_ocr_controller = module.gaze_ocr_controller
                    break
            
            if not gaze_ocr_controller:
                actions.user.connect_ocr_eye_tracker()
                return {}
                
            # Get screen contents
            gaze_ocr_controller.read_nearby()
            contents = gaze_ocr_controller.latest_screen_contents()
            
            # Extract all text items with coordinates
            text_items = []
            for line in contents.result.lines:
                for word in line.words:
                    text_items.append({
                        'text': word.text,
                        'x': word.left + word.width // 2,
                        'y': word.top + word.height // 2,
                        'left': word.left,
                        'top': word.top,
                        'width': word.width,
                        'height': word.height
                    })
            
            # Group items into columns based on X coordinates
            column_threshold = settings.get("user.grid_column_threshold")
            row_threshold = settings.get("user.grid_row_threshold")
            
            # Sort by X coordinate to identify columns
            text_items.sort(key=lambda item: item['x'])
            columns = []
            
            for item in text_items:
                # Find existing column or create new one
                placed = False
                for column in columns:
                    if abs(item['x'] - column[0]['x']) <= column_threshold:
                        column.append(item)
                        placed = True
                        break
                        
                if not placed:
                    columns.append([item])
            
            # Sort items within each column by Y coordinate
            for column in columns:
                column.sort(key=lambda item: item['y'])
            
            # Sort columns by X coordinate
            columns.sort(key=lambda column: column[0]['x'])
            
            grid_info = {
                'columns': columns,
                'column_count': len(columns),
                'text_items': text_items
            }
            
            print(f"Detected grid structure: {len(columns)} columns")
            for i, column in enumerate(columns):
                print(f"Column {i}: {[item['text'] for item in column]}")
            
            actions.user.connect_ocr_eye_tracker()
            return grid_info
            
        except Exception as e:
            print(f"Error analyzing grid structure: {str(e)}")
            actions.user.connect_ocr_eye_tracker()
            return {}

    def find_grid_position(target_text: str, grid_info: dict) -> tuple:
        """Find column and row index of target text in grid"""
        if not grid_info.get('columns'):
            return None, None
            
        for col_idx, column in enumerate(grid_info['columns']):
            for row_idx, item in enumerate(column):
                if target_text.lower() in item['text'].lower():
                    return col_idx, row_idx
                    
        return None, None


    def find_current_position(highlight_image: str, grid_info: dict) -> tuple:
        """Find current column and row index based on highlight position"""
        try:
            # Get highlight coordinates
            highlight_coords = actions.user.mouse_helper_find_template_relative(
                f"{images_to_click_location}{highlight_image}"
            )
            if not highlight_coords:
                return None, None
                
            highlight_rect = highlight_coords[0]
            highlight_center = (highlight_rect.x + highlight_rect.width//2, highlight_rect.y + highlight_rect.height//2)
            
            # Find closest text item to highlight
            min_distance = float('inf')
            closest_col, closest_row = None, None
            
            for col_idx, column in enumerate(grid_info['columns']):
                for row_idx, item in enumerate(column):
                    distance = ((item['x'] - highlight_center[0]) ** 2 + (item['y'] - highlight_center[1]) ** 2) ** 0.5
                    if distance < min_distance:
                        min_distance = distance
                        closest_col, closest_row = col_idx, row_idx
            
            print(f"Current position: column {closest_col}, row {closest_row}")
            return closest_col, closest_row
            
        except Exception as e:
            print(f"Error finding current position: {str(e)}")
            return None, None

    def navigate_step_grid(target_text: str, highlight_image: str, use_wasd: bool, max_steps: int = None, action_button: str = None) -> bool:
        """Grid-aware navigation step - move column first, then row"""
        global navigation_steps_taken, last_direction_pressed
        
        # No step limits for main navigation
            
        try:
            # Analyze grid structure
            grid_info = actions.user.analyze_grid_structure()
            if not grid_info.get('columns'):
                print("Could not detect grid structure, falling back to unified navigation")
                return actions.user.navigate_step(target_text, highlight_image, use_wasd, max_steps, False, action_button)
            
            # Find target and current positions in grid
            target_col, target_row = actions.user.find_grid_position(target_text, grid_info)
            current_col, current_row = actions.user.find_current_position(highlight_image, grid_info)
            
            if target_col is None or current_col is None:
                print("Could not find positions in grid, falling back to unified navigation")
                return actions.user.navigate_step(target_text, highlight_image, use_wasd, max_steps, False, action_button)
            
            print(f"Grid navigation: current ({current_col},{current_row}) -> target ({target_col},{target_row})")
            
            # Check if we've reached the target
            if current_col == target_col and current_row == target_row:
                if action_button:
                    print(f"Reached target! Pressing action button: {action_button}")
                    actions.key(action_button)
                    actions.user.stop_continuous_navigation()
                    return True
                else:
                    print("Reached target!")
                    actions.user.stop_continuous_navigation()
                    return True
            
            # Grid navigation strategy: column first, then row
            if current_col != target_col:
                # Move horizontally to correct column
                if target_col > current_col:
                    key_to_press = "d" if use_wasd else "right"
                    print(f"Moving right to column {target_col}")
                else:
                    key_to_press = "a" if use_wasd else "left"
                    print(f"Moving left to column {target_col}")
                    
                actions.key(key_to_press)
                last_direction_pressed = key_to_press
                
            elif current_row != target_row:
                # Move vertically to correct row (only when in correct column)
                if target_row > current_row:
                    key_to_press = "s" if use_wasd else "down"
                    print(f"Moving down to row {target_row}")
                else:
                    key_to_press = "w" if use_wasd else "up"
                    print(f"Moving up to row {target_row}")
                    
                actions.key(key_to_press)
                last_direction_pressed = key_to_press
            
            # Increment step counter
            navigation_steps_taken += 1
            return False  # Continue navigation
            
        except Exception as e:
            print(f"Grid navigation step error: {str(e)}")
            actions.user.stop_continuous_navigation()
            return False

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

    def find_template_flexible(image_name: str, thresholds: list = None, search_region: tuple = None) -> tuple:
        """Find template using flexible matching with multiple thresholds and optional region limiting"""
        if thresholds is None:
            thresholds = [0.7, 0.75, 0.8, 0.85, 0.9]
            
        image_path = f"{images_to_click_location}{image_name}"
        
        for threshold in thresholds:
            try:
                print(f"Trying template match with threshold {threshold}")
                
                # Use Talon's locate function directly with custom threshold
                import talon.experimental.locate as locate
                
                matches = locate.locate(image_path, threshold=threshold)
                    
                if matches:
                    # Filter matches by region if specified (left_x, top_y, right_x, bottom_y)
                    valid_matches = []
                    for match in matches:
                        center_x = match.x + match.width // 2
                        center_y = match.y + match.height // 2
                        
                        if search_region:
                            left_x, top_y, right_x, bottom_y = search_region
                            if left_x <= center_x <= right_x and top_y <= center_y <= bottom_y:
                                valid_matches.append((center_x, center_y))
                                print(f"Found template at ({center_x}, {center_y}) with threshold {threshold} (within region)")
                            else:
                                print(f"Rejected template at ({center_x}, {center_y}) - outside region {search_region}")
                        else:
                            valid_matches.append((center_x, center_y))
                            print(f"Found template at ({center_x}, {center_y}) with threshold {threshold}")
                    
                    if valid_matches:
                        return valid_matches[0]  # Return first valid match
                        
            except Exception as e:
                print(f"Error with threshold {threshold}: {str(e)}")
                continue
        
        print(f"Could not find template '{image_name}' with any threshold{' in specified region' if search_region else ''}")
        return None

    def find_template_flexible_menu_region(image_name: str) -> tuple:
        """Find template in menu region (left side of screen) using flexible matching"""
        # Menu region: left=0, top=600, right=400, bottom=900 (approximate battle menu area)
        menu_region = (0, 600, 400, 900)
        return actions.user.find_template_flexible(image_name, None, menu_region)

    def calculate_distance(pos1: tuple, pos2: tuple) -> float:
        """Calculate distance between two coordinate points"""
        x_diff = pos1[0] - pos2[0]
        y_diff = pos1[1] - pos2[1]
        return (x_diff ** 2 + y_diff ** 2) ** 0.5

    def find_coordinate_clusters(positions: list, cluster_radius: int = 20) -> list:
        """Group coordinates into clusters based on proximity"""
        if not positions:
            return []
            
        clusters = []
        for pos in positions:
            # Find if this position belongs to an existing cluster
            placed = False
            for cluster in clusters:
                # Check if within cluster radius of any position in cluster
                for cluster_pos in cluster:
                    distance = ((pos[0] - cluster_pos[0]) ** 2 + (pos[1] - cluster_pos[1]) ** 2) ** 0.5
                    if distance <= cluster_radius:
                        cluster.append(pos)
                        placed = True
                        break
                if placed:
                    break
                    
            if not placed:
                clusters.append([pos])
        
        print(f"Found {len(clusters)} coordinate clusters from {len(positions)} positions")
        for i, cluster in enumerate(clusters):
            centroid_x = sum(p[0] for p in cluster) / len(cluster)
            centroid_y = sum(p[1] for p in cluster) / len(cluster)
            print(f"Cluster {i}: {len(cluster)} positions, centroid: ({centroid_x:.1f}, {centroid_y:.1f})")
            
        return clusters

    def detect_repeating_pattern(position_history: list, tolerance: int = 25) -> tuple:
        """Detect repeating patterns of any length in position history"""
        if len(position_history) < 4:
            return False, []
        
        # Try different pattern lengths from 2 up to half the history size
        for pattern_length in range(2, len(position_history) // 2 + 1):
            # Get the most recent pattern
            recent_pattern = position_history[-pattern_length:]
            
            # Look backwards through history to find this exact pattern
            for start_idx in range(len(position_history) - pattern_length * 2, -1, -1):
                candidate_pattern = position_history[start_idx:start_idx + pattern_length]
                
                if actions.user.patterns_match(recent_pattern, candidate_pattern, tolerance):
                    print(f"PATTERN DETECTED: Length {pattern_length} pattern repeating")
                    print(f"Pattern: {' -> '.join([f'({p[0]:.0f},{p[1]:.0f})' for p in recent_pattern])}")
                    return True, recent_pattern
        
        return False, []

    def patterns_match(pattern1: list, pattern2: list, tolerance: int = 25) -> bool:
        """Check if two position patterns match within tolerance"""
        if len(pattern1) != len(pattern2):
            return False
        
        for i in range(len(pattern1)):
            distance = actions.user.calculate_distance(pattern1[i], pattern2[i])
            if distance > tolerance:
                return False
        return True

    def find_closest_cluster_to_target(clusters: list, target_coords: tuple) -> tuple:
        """Find the cluster whose centroid is closest to the target"""
        if not clusters:
            return None
            
        closest_centroid = None
        min_distance = float('inf')
        
        for cluster in clusters:
            # Calculate cluster centroid
            centroid_x = sum(p[0] for p in cluster) / len(cluster)
            centroid_y = sum(p[1] for p in cluster) / len(cluster)
            centroid = (centroid_x, centroid_y)
            
            # Calculate distance to target
            distance = ((centroid[0] - target_coords[0]) ** 2 + (centroid[1] - target_coords[1]) ** 2) ** 0.5
            
            print(f"Cluster centroid {centroid} distance to target {target_coords}: {distance:.1f}px")
            
            if distance < min_distance:
                min_distance = distance
                closest_centroid = centroid
        
        print(f"Selected closest centroid: {closest_centroid} (distance: {min_distance:.1f}px)")
        return closest_centroid

    def navigate_step(target_text: str, highlight_image: str, use_wasd: bool, max_steps: int = None, extra_step: bool = False, action_button: str = None) -> bool:
        """Single navigation step - check proximity and move if needed"""
        global navigation_steps_taken, last_direction_pressed, cursor_position_history
        
        # Check navigation mode - use grid navigation if enabled
        navigation_mode = settings.get("user.navigation_mode")
        if navigation_mode == "grid":
            return actions.user.navigate_step_grid(target_text, highlight_image, use_wasd, max_steps, action_button)
        
        # No step limits for main navigation
            
        try:
            # Get current coordinates
            text_coords = actions.user.get_text_coordinates(target_text)
            if not text_coords:
                print(f"Could not find text: {target_text}")
                actions.user.stop_continuous_navigation()
                return False

            # Try flexible template matching first, fall back to standard method
            highlight_center = actions.user.find_template_flexible(highlight_image)
            if not highlight_center:
                # Fallback to original method
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
                
            # Enhanced loop detection with tiebreaker mode - detect repeating patterns of any length
            if len(cursor_position_history) >= 4:
                # Robust pattern detection: find any repeating sequence of positions
                pattern_detected, detected_pattern = actions.user.detect_repeating_pattern(cursor_position_history)
                
                if pattern_detected:
                    print(f"TIEBREAKER MODE: Repeating pattern detected!")
                    print(f"Pattern: {' -> '.join([f'({p[0]:.0f},{p[1]:.0f})' for p in detected_pattern])}")
                    print(f"Analyzing coordinate clusters to find closest reachable position...")
                    
                    # Find coordinate clusters from position history
                    clusters = actions.user.find_coordinate_clusters(cursor_position_history, 25)
                    
                    if clusters:
                        # Find cluster closest to target
                        closest_centroid = actions.user.find_closest_cluster_to_target(clusters, text_coords)
                        
                        if closest_centroid:
                            # Check if we're already at the closest position
                            distance_to_closest = ((highlight_center[0] - closest_centroid[0]) ** 2 + (highlight_center[1] - closest_centroid[1]) ** 2) ** 0.5
                            
                            if distance_to_closest <= 30:  # Within 30px of closest position
                                print(f"TIEBREAKER SUCCESS: At closest reachable position to target!")
                                print(f"Current: {highlight_center}, Closest centroid: {closest_centroid}, Target: {text_coords}")
                                if action_button:
                                    print(f"Pressing action button: {action_button}")
                                    actions.key(action_button)
                                actions.user.stop_continuous_navigation()
                                return True
                            else:
                                print(f"Navigating to closest centroid: {closest_centroid}")
                                # Navigate toward the closest centroid instead of original target
                                text_coords = closest_centroid  # Override target for this step
                    
                    # If no clusters found, fall back to original behavior
                    if not clusters:
                        print(f"No clusters found, stopping navigation")
                        actions.user.stop_continuous_navigation()
                        return False
            
            # Check proximity using configurable navigation mode
            x_diff = text_coords[0] - highlight_center[0]
            y_diff = text_coords[1] - highlight_center[1]
            
            # Alignment-based mode switching: lock into directional mode when aligned
            alignment_threshold = 60  # pixels - how close is "aligned"
            
            # Check for vertical alignment (same column)
            if abs(x_diff) <= alignment_threshold:
                print(f"Vertical alignment detected (X diff: {x_diff:.1f} <= {alignment_threshold}) - locking to vertical mode")
                navigation_mode = "vertical"
            # Check for horizontal alignment (same row) 
            elif abs(y_diff) <= alignment_threshold:
                print(f"Horizontal alignment detected (Y diff: {y_diff:.1f} <= {alignment_threshold}) - locking to horizontal mode")
                navigation_mode = "horizontal"
            # Otherwise use configured mode
            else:
                if 'navigation_mode' not in locals():
                    navigation_mode = settings.get("user.navigation_mode")
                print(f"No alignment detected - using {navigation_mode} mode")
            
            
            print(f"=== ALIGNMENT-BASED NAVIGATION ===")
            print(f"Target '{target_text}' coords: {text_coords}")
            print(f"Cursor coords: {highlight_center}")
            print(f"X diff: {x_diff:.1f} (positive = target is RIGHT)")
            print(f"Y diff: {y_diff:.1f} (positive = target is DOWN)")
            print(f"Selected mode: {navigation_mode}")
            
            if navigation_mode == "vertical":
                # Vertical mode - tight Y check only
                is_on_target = abs(y_diff) <= 25
                print(f"Vertical mode - Y close: {abs(y_diff) <= 25}, On target: {is_on_target}")
            elif navigation_mode == "horizontal":
                # Horizontal mode - tight X check only  
                is_on_target = abs(x_diff) <= 25
                print(f"Horizontal mode - X close: {abs(x_diff) <= 25}, On target: {is_on_target}")
            else:
                # Unified mode - both X and Y proximity with cursor-awareness
                proximity_x = settings.get("user.highlight_proximity_x")
                proximity_y = settings.get("user.highlight_proximity_y")
                
                # Cursor-aware logic: cursor should be to the left of or close to the target text
                # More lenient if cursor is to the left (negative x_diff), tighter if to the right
                if x_diff <= 0:  # Cursor is to the left of target (expected)
                    x_close = abs(x_diff) <= proximity_x
                else:  # Cursor is to the right of target (unexpected, be more strict)
                    x_close = abs(x_diff) <= proximity_x * 0.5
                    
                y_close = abs(y_diff) <= proximity_y
                is_on_target = x_close and y_close
                print(f"Unified mode - X diff: {x_diff:.1f}, Y diff: {y_diff:.1f}, X close: {x_close}, Y close: {y_close}, On target: {is_on_target}")
            
            if is_on_target:
                if action_button:
                    print(f"Reached target! Target: {text_coords}, Cursor: {highlight_center}")
                    print(f"Final differences - X: {x_diff:.1f}, Y: {y_diff:.1f}, Mode: {navigation_mode}")
                    print(f"Pressing action button: {action_button}")
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
            elif navigation_mode == "horizontal":
                # Horizontal mode - prioritize horizontal movement
                if abs(x_diff) > 10:  # Prioritize horizontal if more than 10px away
                    if x_diff > 0:
                        key_to_press = "d" if use_wasd else "right"
                        print(f"Pressing {key_to_press} (right) - horizontal priority")
                        actions.key(key_to_press)
                        last_direction_pressed = key_to_press
                    else:
                        key_to_press = "a" if use_wasd else "left"
                        print(f"Pressing {key_to_press} (left) - horizontal priority")
                        actions.key(key_to_press)
                        last_direction_pressed = key_to_press
                else:
                    # Only move vertically when horizontally aligned
                    if y_diff > 0:
                        key_to_press = "s" if use_wasd else "down"
                        print(f"Pressing {key_to_press} (down) - horizontal aligned")
                        actions.key(key_to_press)
                        last_direction_pressed = key_to_press
                    else:
                        key_to_press = "w" if use_wasd else "up"
                        print(f"Pressing {key_to_press} (up) - horizontal aligned")
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
        global navigation_job, navigation_steps_taken, last_direction_pressed, cursor_position_history
        
        # Stop any existing navigation
        actions.user.stop_continuous_navigation()
        
        # Reset step counter, direction tracking, and position history
        navigation_steps_taken = 0
        last_direction_pressed = None
        cursor_position_history = []
        
        # Start new navigation job with error handling
        navigation_interval = settings.get("user.navigation_interval")
        
        def safe_navigate_step():
            try:
                return actions.user.navigate_step(target_text, highlight_image, use_wasd, max_steps, extra_step, action_button)
            except Exception as e:
                print(f"Navigation step error (continuing): {str(e)}")
                return False  # Continue navigation despite errors
        
        navigation_job = cron.interval(f"{navigation_interval}ms", safe_navigate_step)
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

    def test_grid_analysis() -> None:
        """Test grid structure analysis"""
        grid_info = actions.user.analyze_grid_structure()
        if grid_info.get('columns'):
            print(f"Grid analysis successful: {len(grid_info['columns'])} columns detected")
            for i, column in enumerate(grid_info['columns']):
                print(f"Column {i}: {[item['text'] for item in column]}")
        else:
            print("No grid structure detected")

    def test_grid_navigation(target_text: str, highlight_image: str = "chained_battle_border.png", max_steps: int = 5) -> None:
        """Test grid navigation with safety limits"""
        print(f"Testing grid navigation to '{target_text}' with max {max_steps} steps")
        actions.user.navigate_step_grid(target_text, highlight_image, True, max_steps, None)