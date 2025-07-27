"""
Template matching and cursor detection for pathfinding system.

Handles cursor detection using game-specific templates and flexible threshold matching.
"""

from talon import Module, actions, settings
import os

mod = Module()

# Path to images for template matching
images_to_click_location = "/Users/jarrod/.talon/user/jarrod/gaming/images_to_click/"

# Global variable for optimization
last_successful_cursor_file = None

@mod.action_class
class TemplateMatchingActions:
    def find_cursor_flexible(cursor_directory: str = None, thresholds: list = None, search_region: tuple = None) -> tuple:
        """Find cursor using game-specific cursor directory with multiple cursor variations"""
        global last_successful_cursor_file
        
        if thresholds is None:
            thresholds = [0.9, 0.85]
            
        # Determine cursor directory and path
        if not cursor_directory:
            cursor_directory = settings.get("user.cursor_directory")
            
        if cursor_directory:
            # Use game-specific cursor directory
            cursors_base_path = f"/Users/jarrod/.talon/user/jarrod/gaming/cursors/{cursor_directory}/"
            
            if not os.path.exists(cursors_base_path):
                print(f"ERROR: Cursor directory not found: {cursors_base_path}")
                return None
                
            # Get all image files in the cursor directory
            cursor_files = []
            for file in os.listdir(cursors_base_path):
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    cursor_files.append(file)
                    
            if not cursor_files:
                print(f"ERROR: No cursor images found in {cursors_base_path}")
                return None
                
            print(f"Trying {len(cursor_files)} cursor variations from {cursor_directory}/")
            
            # Optimization: Try last successful cursor first if it exists
            cursor_files_to_try = []
            
            if last_successful_cursor_file and last_successful_cursor_file in cursor_files:
                # Try last successful cursor first
                cursor_files_to_try.append(last_successful_cursor_file)
                print(f"OPTIMIZATION: Trying last successful cursor first: {last_successful_cursor_file}")
                
                # Add remaining cursor files (excluding the last successful one)
                remaining_files = [f for f in cursor_files if f != last_successful_cursor_file]
                cursor_files_to_try.extend(remaining_files)
            else:
                # No previous successful cursor or it's not in current directory
                cursor_files_to_try = cursor_files
            
            # Try cursor files in optimized order
            for cursor_file in cursor_files_to_try:
                cursor_path = cursors_base_path + cursor_file
                print(f"Trying cursor: {cursor_file}")
                
                # Try each threshold for this cursor
                for threshold in thresholds:
                    try:
                        print(f"  Trying threshold {threshold}")
                        
                        import talon.experimental.locate as locate
                        matches = locate.locate(cursor_path, threshold=threshold)
                        
                        if matches:
                            if len(matches) == 1:
                                # Single match - best case
                                match = matches[0]
                                center_x = match.x + match.width // 2
                                # Use bottom of middle third to prevent false proximity when cursor overlaps target
                                center_y = match.y + 2 * match.height // 3
                                
                                if search_region:
                                    left_x, top_y, right_x, bottom_y = search_region
                                    if left_x <= center_x <= right_x and top_y <= center_y <= bottom_y:
                                        result = (center_x, center_y)
                                        print(f"SUCCESS: Found single cursor using {cursor_file} at {result}")
                                        last_successful_cursor_file = cursor_file  # Update tracking
                                        return result
                                else:
                                    result = (center_x, center_y)
                                    print(f"SUCCESS: Found single cursor using {cursor_file} at {result}")
                                    last_successful_cursor_file = cursor_file  # Update tracking
                                    return result
                            else:
                                # Multiple matches - take first one and warn
                                print(f"  WARNING: Multiple matches ({len(matches)}) for {cursor_file}, using first")
                                match = matches[0]
                                center_x = match.x + match.width // 2
                                # Use bottom of middle third to prevent false proximity when cursor overlaps target
                                center_y = match.y + 2 * match.height // 3
                                
                                if search_region:
                                    left_x, top_y, right_x, bottom_y = search_region
                                    if left_x <= center_x <= right_x and top_y <= center_y <= bottom_y:
                                        result = (center_x, center_y)
                                        print(f"SUCCESS: Found cursor using {cursor_file} at {result} (first of {len(matches)})")
                                        last_successful_cursor_file = cursor_file  # Update tracking
                                        return result
                                else:
                                    result = (center_x, center_y)
                                    print(f"SUCCESS: Found cursor using {cursor_file} at {result} (first of {len(matches)})")
                                    last_successful_cursor_file = cursor_file  # Update tracking
                                    return result
                                
                    except Exception as e:
                        print(f"  Error with {cursor_file} at threshold {threshold}: {e}")
                        continue
                    
            print(f"No cursor found using any variation in {cursor_directory}/")
            return None
        else:
            # Fallback to original highlight_image setting
            highlight_image = settings.get("user.highlight_image")
            if highlight_image:
                print(f"No cursor directory set, using highlight_image: {highlight_image}")
                return actions.user.find_template_flexible(highlight_image, thresholds, search_region)
            else:
                print("ERROR: No cursor directory or highlight_image configured")
                return None

    def find_template_flexible(image_name: str, thresholds: list = None, search_region: tuple = None) -> tuple:
        """Find template using flexible matching with multiple thresholds and optional region limiting"""
        if thresholds is None:
            thresholds = [0.9]  # Use high threshold for cursor variations
            
        image_path = f"{images_to_click_location}{image_name}"
        
        for threshold in thresholds:
            try:
                print(f"Trying template match with threshold {threshold}")
                
                # Use Talon's locate function directly with custom threshold
                import talon.experimental.locate as locate
                
                matches = locate.locate(image_path, threshold=threshold)
                    
                if matches:
                    # Multi-cursor detection warning
                    if len(matches) > 1:
                        print(f"WARNING: Multiple cursor matches detected ({len(matches)} matches) at threshold {threshold}")
                        print(f"This may indicate template matching issues that need investigation!")
                        for i, match in enumerate(matches):
                            center_x = match.x + match.width // 2
                            # Use bottom of middle third to prevent false proximity when cursor overlaps target
                            center_y = match.y + 2 * match.height // 3
                            print(f"  Cursor match {i+1}: ({center_x}, {center_y})")
                    
                    # Filter matches by region if specified (left_x, top_y, right_x, bottom_y)
                    valid_matches = []
                    for match in matches:
                        center_x = match.x + match.width // 2
                        # Use bottom of middle third to prevent false proximity when cursor overlaps target
                        center_y = match.y + 2 * match.height // 3
                        
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
                        if len(valid_matches) > 1:
                            print(f"WARNING: Multiple valid cursor matches ({len(valid_matches)}) after region filtering!")
                            print(f"Selecting first match: {valid_matches[0]}")
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