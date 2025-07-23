"""
Menu navigation using OCR text detection and image template matching.
Designed for games that don't support mouse input but have keyboard-based menu navigation.
"""

from talon import Module, actions, app, cron, settings
import os
import json
from talon.types import Rect as TalonRect

# Import RapidFuzz for fuzzy text matching (same as talon-gaze-ocr)
try:
    from rapidfuzz import fuzz
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    print("RapidFuzz not available - fuzzy matching disabled")
    RAPIDFUZZ_AVAILABLE = False

mod = Module()

# Path to images for template matching
images_to_click_location = "/Users/jarrod/.talon/user/jarrod/gaming/images_to_click/"

# Global variables for navigation job
navigation_job = None
navigation_steps_taken = 0
last_direction_pressed = None
cursor_position_history = []  # Track cursor positions to detect loops
stable_position_history = []  # Track only stable/settled cursor positions
position_timing = {}  # Track when cursor first arrived at each position
current_target_width = 0  # Width of current target text for victory line calculation

# Basic homophones for common speech recognition errors (fallback if community system unavailable)
BASIC_HOMOPHONES = {
    "ok": ["ok", "okay", "0k"],
    "okay": ["ok", "okay", "0k"],
    "0k": ["ok", "okay", "0k"],
    "to": ["to", "two", "2"],
    "two": ["to", "two", "2"],
    "2": ["to", "two", "2"],
    "too": ["to", "two", "2", "too"],
    "for": ["for", "four", "4"],
    "four": ["for", "four", "4"],
    "4": ["for", "four", "4"],
}

def get_homophones_for_word(word: str) -> list:
    """Get homophones using community system with fallback to basic set"""
    try:
        # Try community homophones system first
        homophones = actions.user.homophones_get(word.lower())
        if homophones and len(homophones) > 1:
            print(f"Using community homophones for '{word}': {homophones}")
            return homophones
    except (KeyError, AttributeError) as e:
        print(f"Community homophones not available for '{word}': {e}")
    
    # Fallback to our basic set
    basic_homophones = BASIC_HOMOPHONES.get(word.lower(), [word])
    if len(basic_homophones) > 1:
        print(f"Using basic homophones for '{word}': {basic_homophones}")
    return basic_homophones

def normalize_text_for_fuzzy_matching(text: str) -> str:
    """Normalize text for fuzzy matching (same as talon-gaze-ocr)"""
    return text.lower().replace("\u2019", "'")

def score_word_fuzzy(candidate_text: str, target_text: str, threshold: float) -> float:
    """Score a word using fuzzy matching with community homophone support"""
    if not RAPIDFUZZ_AVAILABLE:
        return 0.0
        
    candidate_normalized = normalize_text_for_fuzzy_matching(candidate_text)
    target_normalized = normalize_text_for_fuzzy_matching(target_text)
    
    # Get homophones using community system with fallback
    homophones = get_homophones_for_word(target_normalized)
    
    # Ensure target is included (normalize homophones to lowercase)
    homophones_normalized = [normalize_text_for_fuzzy_matching(h) for h in homophones]
    if target_normalized not in homophones_normalized:
        homophones_normalized.append(target_normalized)
    
    # Try matching against all homophones, return best score
    best_score = 0.0
    best_homophone = None
    
    for homophone in homophones_normalized:
        try:
            score = fuzz.ratio(
                homophone,
                candidate_normalized,
                score_cutoff=threshold / 2 * 100  # Initial cutoff at 50% of threshold
            )
            if score > best_score * 100:  # Convert back to compare
                best_score = score / 100.0
                best_homophone = homophone
        except Exception as e:
            print(f"Fuzzy matching error for '{homophone}' vs '{candidate_normalized}': {e}")
            continue
    
    if best_homophone and best_score > 0:
        print(f"    Best match: homophone '{best_homophone}' vs candidate '{candidate_normalized}' = {best_score:.2f}")
    
    return best_score

# Settings for menu navigation
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

mod.setting(
    "uses_wasd",
    type=bool,
    default=True,
    desc="Use WASD keys for navigation instead of arrow keys"
)

mod.setting(
    "position_stability_threshold",
    type=int,
    default=1400,
    desc="Time in milliseconds cursor must remain at position to be considered stable/settled (should be 2x navigation interval)"
)

mod.setting(
    "cursor_directory",
    type=str,
    default="",
    desc="Name of cursor directory under cursors/ containing game-specific cursor templates (e.g., 'chained_echoes')"
)

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

    def test_navigate_to_text_with_highlight(target_text: str, highlight_image: str = None):
        """Test function: Navigate using coordinates of text vs highlight image"""
        try:
            # Use configured highlight image if none provided
            if highlight_image is None:
                highlight_image = settings.get("user.highlight_image")
            
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
                # Find ALL matching text instances, then pick the best one
                text_matches = []
                all_words = []  # Store all words for potential fuzzy matching
                
                for line_idx, line in enumerate(contents.result.lines):
                    for word_idx, word in enumerate(line.words):
                        print(f"Line {line_idx}, Word {word_idx}: '{word.text}' at ({word.left}, {word.top})")
                        
                        # Store word for potential fuzzy matching
                        word_info = {
                            'coords': (word.left, word.top + word.height//2),
                            'text': word.text,
                            'width': word.width,
                            'line': line_idx,
                            'word': word_idx
                        }
                        all_words.append(word_info)
                        
                        # Try exact matching first (current behavior)
                        if target_text.lower() in word.text.lower():
                            text_matches.append(word_info)
                
                # If exact matches found, use them
                if text_matches:
                    print(f"Found {len(text_matches)} exact matches for '{target_text}'")
                elif settings.get("user.menu_enable_fuzzy_matching") and RAPIDFUZZ_AVAILABLE and all_words:
                    # Try fuzzy matching as fallback
                    print(f"No exact matches for '{target_text}', trying fuzzy matching...")
                    fuzzy_threshold = settings.get("user.menu_fuzzy_threshold")
                    fuzzy_matches = []
                    
                    for word_info in all_words:
                        score = score_word_fuzzy(word_info['text'], target_text, fuzzy_threshold)
                        print(f"  Testing '{word_info['text']}' vs '{target_text}': score {score:.2f} (threshold: {fuzzy_threshold:.2f})")
                        if score >= fuzzy_threshold:
                            word_info['fuzzy_score'] = score
                            fuzzy_matches.append(word_info)
                            print(f"  ✓ Fuzzy match: '{word_info['text']}' (score: {score:.2f})")
                    
                    if fuzzy_matches:
                        # Sort by score (best first) and use fuzzy matches
                        fuzzy_matches.sort(key=lambda x: x['fuzzy_score'], reverse=True)
                        text_matches = fuzzy_matches
                        print(f"Found {len(text_matches)} fuzzy matches for '{target_text}' (best score: {text_matches[0]['fuzzy_score']:.2f})")
                    else:
                        print(f"No fuzzy matches found for '{target_text}' above threshold {fuzzy_threshold:.2f}")
                
                if text_matches:
                    global current_target_width
                    
                    if len(text_matches) == 1:
                        # Single match - use it
                        match = text_matches[0]
                        print(f"Found single '{target_text}' at center coordinates: {match['coords']}")
                        current_target_width = match['width']
                        actions.user.connect_ocr_eye_tracker()
                        return match['coords']
                    else:
                        # Multiple matches - pick closest to current cursor
                        print(f"Found {len(text_matches)} instances of '{target_text}':")
                        for i, match in enumerate(text_matches):
                            print(f"  {i+1}. '{match['text']}' at {match['coords']} (Line {match['line']}, Word {match['word']})")
                        
                        # Get current cursor position to choose closest text
                        cursor_pos = actions.user.find_cursor_flexible()
                        if cursor_pos:
                            best_match = None
                            min_distance = float('inf')
                            
                            for match in text_matches:
                                distance = actions.user.calculate_distance(cursor_pos, match['coords'])
                                print(f"  Distance from cursor {cursor_pos} to '{match['text']}' at {match['coords']}: {distance:.1f}px")
                                if distance < min_distance:
                                    min_distance = distance
                                    best_match = match
                            
                            if best_match:
                                print(f"Selected closest '{target_text}' at {best_match['coords']} (distance: {min_distance:.1f}px)")
                                current_target_width = best_match['width']
                                actions.user.connect_ocr_eye_tracker()
                                return best_match['coords']
                        else:
                            # No cursor found, use first match
                            match = text_matches[0]
                            print(f"No cursor found, using first '{target_text}' at {match['coords']}")
                            current_target_width = match['width']
                            actions.user.connect_ocr_eye_tracker()
                            return match['coords']
                
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

    def find_cursor_flexible(cursor_directory: str = None, thresholds: list = None, search_region: tuple = None) -> tuple:
        """Find cursor using game-specific cursor directory with multiple cursor variations"""
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
            
            # Just return first successful cursor match for now - revert to simple approach
            for cursor_file in cursor_files:
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
                                        return result
                                else:
                                    result = (center_x, center_y)
                                    print(f"SUCCESS: Found single cursor using {cursor_file} at {result}")
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
                                        return result
                                else:
                                    result = (center_x, center_y)
                                    print(f"SUCCESS: Found cursor using {cursor_file} at {result} (first of {len(matches)})")
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

    def calculate_distance(pos1: tuple, pos2: tuple) -> float:
        """Calculate distance between two coordinate points"""
        x_diff = pos1[0] - pos2[0]
        y_diff = pos1[1] - pos2[1]
        return (x_diff ** 2 + y_diff ** 2) ** 0.5

    def check_cursor_intersects_victory_line(cursor_pos: tuple, text_coords: tuple, text_width: float, cursor_size: tuple = (16, 54), left_extension: int = 50) -> bool:
        """Check if horizontal victory line extending left from text intersects with cursor rectangle"""
        cursor_x, cursor_y = cursor_pos
        cursor_width, cursor_height = cursor_size
        text_center_x, text_center_y = text_coords
        
        # Estimate text left edge (assuming text_coords is center)
        text_left = text_center_x - text_width // 2
        
        # Calculate cursor rectangle bounds
        cursor_left = cursor_x - cursor_width // 2
        cursor_right = cursor_x + cursor_width // 2  
        cursor_top = cursor_y - cursor_height // 2
        cursor_bottom = cursor_y + cursor_height // 2
        
        # Victory line coordinates
        line_y = text_center_y
        line_x_start = text_left - left_extension
        line_x_end = text_left
        
        # Check if horizontal line intersects cursor rectangle
        line_intersects_horizontally = (line_x_start <= cursor_right and line_x_end >= cursor_left)
        line_intersects_vertically = (cursor_top <= line_y <= cursor_bottom)
        
        victory = line_intersects_horizontally and line_intersects_vertically
        
        print(f"Victory line check: Line Y={line_y}, X=[{line_x_start}, {line_x_end}]")
        print(f"Cursor bounds: X=[{cursor_left}, {cursor_right}], Y=[{cursor_top}, {cursor_bottom}]")
        print(f"Intersects horizontally: {line_intersects_horizontally}, vertically: {line_intersects_vertically}")
        print(f"Victory: {victory}")
        
        return victory

    def add_position_if_stable(current_pos: tuple) -> None:
        """Add position to stable history only if cursor has been there long enough"""
        global stable_position_history, position_timing
        import time
        
        current_time = time.time() * 1000  # Convert to milliseconds
        stability_threshold = settings.get("user.position_stability_threshold")
        
        # Round position to nearest 5 pixels to handle minor template matching variations
        rounded_pos = (round(current_pos[0] / 5) * 5, round(current_pos[1] / 5) * 5)
        
        if rounded_pos in position_timing:
            # Check if position has been stable long enough
            time_at_position = current_time - position_timing[rounded_pos]
            if time_at_position >= stability_threshold:
                # Position is stable - add to stable history if not already there
                if not stable_position_history or stable_position_history[-1] != current_pos:
                    stable_position_history.append(current_pos)
                    print(f"Added stable position: {current_pos} (stable for {time_at_position:.0f}ms)")
                    
                    # Keep stable history manageable (last 8 stable positions)
                    if len(stable_position_history) > 8:
                        stable_position_history.pop(0)
        else:
            # First time at this position - start timing
            position_timing[rounded_pos] = current_time
            
            # Clean up old timing entries to prevent memory buildup
            if len(position_timing) > 20:
                oldest_key = min(position_timing.keys(), key=lambda k: position_timing[k])
                del position_timing[oldest_key]

    def find_closest_stable_position_to_target(target_coords: tuple) -> tuple:
        """Find the stable position from history that is closest to the target coordinates"""
        global stable_position_history
        
        if not stable_position_history:
            print("No stable positions recorded yet")
            return None
            
        closest_pos = None
        min_distance = float('inf')
        
        print(f"Checking {len(stable_position_history)} stable positions against target {target_coords}")
        for pos in stable_position_history:
            distance = actions.user.calculate_distance(pos, target_coords)
            print(f"  Stable position {pos}: distance {distance:.1f}px")
            if distance < min_distance:
                min_distance = distance
                closest_pos = pos
        
        print(f"Found closest stable position to target: {closest_pos} (distance: {min_distance:.1f}px)")
        return closest_pos

    def find_closest_position_to_target(position_history: list, target_coords: tuple) -> tuple:
        """Find the position from history that is closest to the target coordinates"""
        if not position_history:
            return None
            
        closest_pos = None
        min_distance = float('inf')
        
        for pos in position_history:
            distance = actions.user.calculate_distance(pos, target_coords)
            if distance < min_distance:
                min_distance = distance
                closest_pos = pos
        
        print(f"Found closest position to target {target_coords}: {closest_pos} (distance: {min_distance:.1f}px)")
        return closest_pos

    def detect_repeating_pattern(position_history: list, tolerance: int = 25, required_repetitions: int = 2) -> tuple:
        """Detect repeating patterns that occur multiple times in position history"""
        if len(position_history) < 4:  # Need at least 4 positions for meaningful pattern detection
            return False, []
        
        # Try different pattern lengths from 2 up to 1/3 of history size
        for pattern_length in range(2, len(position_history) // 3 + 1):
            # Get the most recent pattern
            recent_pattern = position_history[-pattern_length:]
            
            # Count how many times this pattern appears in the history
            repetition_count = 0
            
            # Look backwards through history to count pattern repetitions
            for start_idx in range(len(position_history) - pattern_length, -1, -pattern_length):
                if start_idx < 0:
                    break
                candidate_pattern = position_history[start_idx:start_idx + pattern_length]
                
                if len(candidate_pattern) == pattern_length and actions.user.patterns_match(recent_pattern, candidate_pattern, tolerance):
                    repetition_count += 1
                else:
                    break  # Stop if pattern doesn't match (no longer continuous repetition)
            
            # Only trigger if pattern repeats the required number of times
            if repetition_count >= required_repetitions:
                print(f"PATTERN DETECTED: Length {pattern_length} pattern repeating {repetition_count} times")
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

            # Try flexible cursor detection first (game-specific cursors), fall back to standard method
            highlight_center = actions.user.find_cursor_flexible()
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
                                actions.key(action_button)
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
            
            # Check proximity using configurable navigation mode
            x_diff = text_coords[0] - highlight_center[0]
            y_diff = text_coords[1] - highlight_center[1]
            
            # Get configurable proximity settings for alignment detection
            proximity_x = settings.get("user.highlight_proximity_x")
            proximity_y = settings.get("user.highlight_proximity_y")
            
            # Alignment-based mode switching: lock into directional mode when aligned
            # Use proximity settings instead of hardcoded values
            
            # Check for vertical alignment (same column)
            if abs(x_diff) <= proximity_x:
                print(f"Vertical alignment detected (X diff: {x_diff:.1f} <= {proximity_x}) - locking to vertical mode")
                navigation_mode = "vertical"
            # Check for horizontal alignment (same row) 
            elif abs(y_diff) <= proximity_y:
                print(f"Horizontal alignment detected (Y diff: {y_diff:.1f} <= {proximity_y}) - locking to horizontal mode")
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
            
            # proximity_x and proximity_y already retrieved above for alignment detection
            
            if navigation_mode == "vertical":
                # Vertical mode - configurable Y check only
                is_on_target = abs(y_diff) <= proximity_y
                print(f"Vertical mode - Y close: {abs(y_diff)} <= {proximity_y}, On target: {is_on_target}")
            elif navigation_mode == "horizontal":
                # Horizontal mode - configurable X check only  
                is_on_target = abs(x_diff) <= proximity_x
                print(f"Horizontal mode - X close: {abs(x_diff)} <= {proximity_x}, On target: {is_on_target}")
            else:
                # Unified mode - use configurable X/Y proximity instead of victory line
                is_on_target = abs(x_diff) <= proximity_x and abs(y_diff) <= proximity_y
                print(f"Unified mode - X close: {abs(x_diff)} <= {proximity_x}, Y close: {abs(y_diff)} <= {proximity_y}, On target: {is_on_target}")
            
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
        global navigation_job, navigation_steps_taken, last_direction_pressed, cursor_position_history, stable_position_history, position_timing
        
        # Stop any existing navigation
        actions.user.stop_continuous_navigation()
        
        # Reset step counter, direction tracking, and position history
        navigation_steps_taken = 0
        last_direction_pressed = None
        cursor_position_history = []
        stable_position_history = []
        position_timing = {}
        
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



    def navigate_to_word(word: str, use_wasd: bool = None, max_steps: int = None, action_button: str = None, use_configured_action: bool = False) -> None:
        """Navigate to any word found via OCR with configurable input method and action"""
        # Always use configured highlight image from settings
        highlight_image = settings.get("user.highlight_image")
        
        # Use configured input method if not specified
        if use_wasd is None:
            use_wasd = settings.get("user.uses_wasd")
            
        # Convert word to proper case for OCR matching - handle TimestampedText objects
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
            
        actions.user.start_continuous_navigation(target_text, highlight_image, use_wasd, max_steps, False, action_button)

    def navigate_to_word_with_action(word: object):
        """Navigate to word using configured input method and press configured action button"""
        actions.user.navigate_to_word(word, None, None, None, True)

    # Backwards compatibility wrappers
    def navigate_to_word_wasd(word: str, max_steps: int = None, action_button: str = None) -> None:
        """Navigate to any word found via OCR using WASD, optionally pressing action button when reached"""
        actions.user.navigate_to_word(word, True, max_steps, action_button, False)

    def navigate_to_word_wasd_with_action(word: str) -> None:
        """Navigate to any word found via OCR using WASD and press the configured action button"""
        actions.user.navigate_to_word(word, True, None, None, True)


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
        actions.user.navigate_step_grid(target_text, highlight_image, True, max_steps, None)

    def debug_all_text_coordinates() -> None:
        """Debug function to list all text coordinates found via OCR"""
        print("=== DEBUG: ALL TEXT COORDINATES ===")
        
        # Disconnect eye tracker and scan full screen
        actions.user.disconnect_ocr_eye_tracker()
        
        try:
            # Find OCR controller
            import sys
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
            import sys
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
            
            # Get current cursor position
            highlight_image = settings.get("user.highlight_image")
            cursor_pos = actions.user.find_cursor_flexible()
            if not cursor_pos:
                print("Could not detect cursor position")
                return
            
            # Get target text coordinates
            target_coords = actions.user.get_text_coordinates(target_text)
            if not target_coords:
                print(f"Could not find text: {target_text}")
                return
                
            print(f"Cursor position: {cursor_pos}")
            print(f"Target '{target_text}' position: {target_coords}")
            
            # Create marker rectangles (small 10x10 rectangles around the points)
            marker_size = 10
            cursor_rect = TalonRect(
                cursor_pos[0] - marker_size//2, 
                cursor_pos[1] - marker_size//2, 
                marker_size, 
                marker_size
            )
            target_rect = TalonRect(
                target_coords[0] - marker_size//2, 
                target_coords[1] - marker_size//2, 
                marker_size, 
                marker_size
            )
            
            # Show markers using talon_ui_helper
            actions.user.marker_ui_show([cursor_rect, target_rect])
            print("Debug markers shown! First marker (a) = Cursor, Second marker (b) = Target")
            
        except Exception as e:
            print(f"Error showing debug markers: {e}")

    def hide_pathfinding_debug_markers() -> None:
        """Hide visual debug markers"""
        try:
            actions.user.marker_ui_hide()
            print("Debug markers hidden")
        except Exception as e:
            print(f"Error hiding debug markers: {e}")