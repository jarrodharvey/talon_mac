"""
OCR text detection and coordinate finding for pathfinding system.

Handles text coordinate detection, fuzzy matching, and homophone support.
"""

from talon import Module, actions, settings

# Import RapidFuzz for fuzzy text matching (same as talon-gaze-ocr)
try:
    from rapidfuzz import fuzz
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    print("RapidFuzz not available - fuzzy matching disabled")
    RAPIDFUZZ_AVAILABLE = False

# Import Jaro-Winkler for phonetic similarity (same as talon-gaze-ocr)
try:
    import jarowinkler
    JAROWINKLER_AVAILABLE = True
except ImportError:
    print("Jaro-Winkler not available - phonetic matching disabled")
    JAROWINKLER_AVAILABLE = False

mod = Module()

# Essential fallback homophones (only when community system unavailable)
BASIC_HOMOPHONES = {
    "to": ["too", "two"],
    "too": ["to", "two"], 
    "two": ["to", "too"],
    "there": ["their", "they're"],
    "their": ["there", "they're"],
    "they're": ["there", "their"],
    "your": ["you're"],
    "you're": ["your"],
    "its": ["it's"],
    "it's": ["its"]
}

# Global variable for text width tracking
current_target_width = 0

def clear_hud_event_log():
    """Clear talon-hud event log to prevent OCR false matches"""
    try:
        import sys
        hud_instance = None

        # Find talon-hud display module
        for module_name, module in sys.modules.items():
            if 'talon_hud' in module_name and 'display' in module_name:
                if hasattr(module, 'hud'):
                    hud_instance = module.hud
                    break

        # Clear event log widget
        if hud_instance and hasattr(hud_instance, 'widget_manager'):
            for widget in hud_instance.widget_manager.widgets:
                if hasattr(widget, 'id') and widget.id == "event_log":
                    if hasattr(widget, 'clear_logs'):
                        widget.clear_logs()
                        print("DEBUG: Cleared HUD event log before OCR scan")
                        return True
                    break
        else:
            print("DEBUG: talon-hud instance not found, skipping log clear")
    except Exception as e:
        print(f"DEBUG: Could not clear HUD logs: {e}")
    return False

def restore_hud_command_echo(command_text: str):
    """Restore command echo to HUD event log after OCR scan"""
    try:
        # Use the hud_add_log action to restore the command echo
        actions.user.hud_add_log("command", command_text)
        print(f"DEBUG: Restored command echo to HUD: '{command_text}'")
    except Exception as e:
        print(f"DEBUG: Could not restore HUD command echo: {e}")

def find_phrase_sequences(target_text: str, ocr_lines, fuzzy_threshold: float = 0.8):
    """Find multi-word phrase sequences in OCR lines using sliding window approach (talon-gaze-ocr method)"""
    target_words = target_text.lower().split()
    if len(target_words) <= 1:
        return []  # Single words should use existing word-based matching
    
    phrase_matches = []
    
    for line_idx, line in enumerate(ocr_lines):
        if len(line.words) < len(target_words):
            continue  # Line too short to contain the phrase
        
        # Sliding window approach: try all possible positions
        for start_idx in range(len(line.words) - len(target_words) + 1):
            candidate_words = line.words[start_idx:start_idx + len(target_words)]
            
            # Check if words are adjacent (only whitespace between them)
            adjacent = True
            for i in range(len(candidate_words) - 1):
                current_word = candidate_words[i]
                next_word = candidate_words[i + 1]
                
                # Words are adjacent if next word starts close to where current word ends
                gap = next_word.left - (current_word.left + current_word.width)
                if gap > 30:  # Allow reasonable whitespace gap (30px)
                    adjacent = False
                    break
            
            if not adjacent:
                continue
            
            # Create candidate phrase text
            candidate_phrase = ' '.join([w.text for w in candidate_words])
            
            # Score the complete phrase using fuzzy matching
            if RAPIDFUZZ_AVAILABLE:
                score = fuzz.ratio(target_text.lower(), candidate_phrase.lower()) / 100.0
                if score >= fuzzy_threshold:
                    # Calculate phrase bounding box (first word top-left to last word bottom-right)
                    first_word = candidate_words[0]
                    last_word = candidate_words[-1]
                    
                    phrase_info = {
                        'coords': (
                            first_word.left,  # Left edge of first word (matches single word behavior)
                            first_word.top + first_word.height // 2  # Vertical center of first word
                        ),
                        'text': candidate_phrase,
                        'width': (last_word.left + last_word.width) - first_word.left,
                        'height': max(first_word.height, last_word.height),
                        'line': line_idx,
                        'word_start': start_idx,
                        'word_count': len(candidate_words),
                        'fuzzy_score': score,
                        'is_phrase': True
                    }
                    phrase_matches.append(phrase_info)
                    print(f"  ✓ Phrase match: '{candidate_phrase}' (score: {score:.2f}) at {phrase_info['coords']}")
    
    return phrase_matches

def get_homophones_for_word(word: str) -> list:
    """Get homophones using community system with fallback to basic set"""
    try:
        # Try community homophones system first
        homophones = actions.user.homophones_get(word.lower())
        if homophones and len(homophones) > 1:
            return homophones
    except:
        pass
    
    # Fallback to basic homophones
    return BASIC_HOMOPHONES.get(word.lower(), [word])

def normalize_text_for_fuzzy_matching(text: str) -> str:
    """Normalize text for fuzzy matching (same as talon-gaze-ocr)"""
    return text.lower().replace("\u2019", "'")

def score_word_fuzzy(candidate_text: str, target_text: str, threshold: float) -> float:
    """Score a word using multi-algorithm fuzzy matching with enhanced homophone support"""
    candidate_normalized = normalize_text_for_fuzzy_matching(candidate_text)
    target_normalized = normalize_text_for_fuzzy_matching(target_text)
    
    # Get homophones using community system with fallback
    homophones = get_homophones_for_word(target_normalized)
    
    # Ensure target is included (normalize homophones to lowercase)
    homophones_normalized = [normalize_text_for_fuzzy_matching(h) for h in homophones]
    if target_normalized not in homophones_normalized:
        homophones_normalized.append(target_normalized)
    
    best_score = 0.0
    best_method = None
    best_homophone = None
    
    # Try each homophone with multiple algorithms
    for homophone in homophones_normalized:
        # 1. Exact match (highest priority)
        if candidate_normalized == homophone:
            print(f"    EXACT match: '{candidate_normalized}' == '{homophone}' = 1.00")
            return 1.0
        
        # 2. Jaro-Winkler similarity (excellent for phonetic matching like fire/file)
        if JAROWINKLER_AVAILABLE:
            try:
                jw_score = jarowinkler.jarowinkler_similarity(candidate_normalized, homophone)
                if jw_score > best_score and jw_score >= 0.75:  # Stricter threshold for phonetic to avoid false positives
                    best_score = jw_score
                    best_method = f"Jaro-Winkler vs '{homophone}'"
                    best_homophone = homophone
            except Exception as e:
                print(f"Jaro-Winkler error for '{homophone}' vs '{candidate_normalized}': {e}")
        
        # 3. RapidFuzz algorithms (if available)
        if RAPIDFUZZ_AVAILABLE:
            try:
                # Standard ratio
                ratio_score = fuzz.ratio(homophone, candidate_normalized) / 100.0
                if ratio_score > best_score and ratio_score >= threshold:
                    best_score = ratio_score
                    best_method = f"Ratio vs '{homophone}'"
                    best_homophone = homophone
                
                # Partial ratio (good for substring matching)
                partial_score = fuzz.partial_ratio(homophone, candidate_normalized) / 100.0
                if partial_score > best_score and partial_score >= threshold:
                    best_score = partial_score
                    best_method = f"Partial ratio vs '{homophone}'"
                    best_homophone = homophone
                
                # Token sort ratio (good for word order independence)
                token_score = fuzz.token_sort_ratio(homophone, candidate_normalized) / 100.0
                if token_score > best_score and token_score >= threshold:
                    best_score = token_score
                    best_method = f"Token sort vs '{homophone}'"
                    best_homophone = homophone
                    
            except Exception as e:
                print(f"RapidFuzz error for '{homophone}' vs '{candidate_normalized}': {e}")
    
    # Debug logging
    if best_score > 0 and best_method:
        print(f"    Best fuzzy match: {best_method} = {best_score:.3f}")
    elif len(homophones_normalized) > 1:
        print(f"    No fuzzy matches above threshold {threshold:.2f} for '{candidate_normalized}' vs homophones {homophones_normalized}")
    
    return best_score

def get_hud_log_exclusion_region():
    """Get the screen region occupied by talon_hud event log to exclude from OCR results"""
    try:
        import sys
        # Find the talon_hud display module and get event log widget position
        for module_name, module in sys.modules.items():
            if 'talon_hud' in module_name and 'display' in module_name:
                if hasattr(module, 'hud') and hasattr(module.hud, 'widget_manager'):
                    for widget in module.hud.widget_manager.widgets:
                        if hasattr(widget, 'id') and widget.id == "event_log":
                            if hasattr(widget, 'x') and hasattr(widget, 'y'):
                                # Return the bounding box of the event log
                                # Add some padding to be safe
                                padding = 20
                                return {
                                    'x': widget.x - padding,
                                    'y': widget.y - padding,
                                    'width': widget.width + padding * 2,
                                    'height': widget.height + padding * 2
                                }
    except Exception as e:
        print(f"DEBUG: Could not get HUD log region: {e}")

    # Fallback to default position if we can't detect it
    # Default is bottom-right: x=1430, y=720, width=450, height=200
    return {'x': 1410, 'y': 700, 'width': 490, 'height': 240}

def filter_hud_log_results(text_matches):
    """Filter out OCR results that are in the HUD log region"""
    hud_region = get_hud_log_exclusion_region()
    print(f"DEBUG: Excluding HUD log region: x={hud_region['x']}, y={hud_region['y']}, w={hud_region['width']}, h={hud_region['height']}")

    filtered_matches = []
    excluded_count = 0

    for match in text_matches:
        coords = match.get('coords', (0, 0))
        x, y = coords

        # Check if this coordinate is inside the HUD log region
        if (hud_region['x'] <= x <= hud_region['x'] + hud_region['width'] and
            hud_region['y'] <= y <= hud_region['y'] + hud_region['height']):
            print(f"DEBUG: Excluded '{match.get('text', '')}' at {coords} (inside HUD log region)")
            excluded_count += 1
        else:
            filtered_matches.append(match)

    if excluded_count > 0:
        print(f"DEBUG: Filtered out {excluded_count} matches from HUD log region, {len(filtered_matches)} remaining")

    return filtered_matches

@mod.action_class
class OCRTextDetectionActions:
    def get_text_coordinates(target_text: str, source_command: str = None):
        """Find coordinates of text using OCR with fuzzy matching support"""
        try:
            # Disconnect eye tracker to scan full screen
            actions.user.disconnect_ocr_eye_tracker()

            # Clear HUD logs before OCR scan
            if source_command:
                clear_hud_event_log()

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
                # PHASE 1: Try phrase sequence matching first (multi-word phrases)
                text_matches = []
                all_words = []  # Store all words for potential fuzzy matching
                
                # Check if this is a multi-word phrase
                target_words = target_text.split()
                if len(target_words) > 1:
                    print(f"Multi-word target detected: '{target_text}' -> {target_words}")
                    fuzzy_threshold = settings.get("user.menu_fuzzy_threshold", 0.8)
                    phrase_matches = find_phrase_sequences(target_text, contents.result.lines, fuzzy_threshold)
                    if phrase_matches:
                        # Sort phrase matches by score (best first)
                        phrase_matches.sort(key=lambda x: x['fuzzy_score'], reverse=True)
                        text_matches = phrase_matches
                        print(f"Found {len(text_matches)} phrase sequence matches for '{target_text}' (best score: {text_matches[0]['fuzzy_score']:.2f})")
                
                # PHASE 2: If no phrase matches, try individual word matching (original behavior)
                if not text_matches:
                    print(f"No phrase matches found, trying individual word matching for '{target_text}'")
                    
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
                        print(f"Found {len(text_matches)} exact word matches for '{target_text}'")
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
                            print(f"Found {len(text_matches)} fuzzy word matches for '{target_text}' (best score: {text_matches[0]['fuzzy_score']:.2f})")
                        else:
                            print(f"No fuzzy matches found for '{target_text}' above threshold {fuzzy_threshold:.2f}")

                # Filter out results in the HUD log region
                if text_matches:
                    text_matches = filter_hud_log_results(text_matches)

                if text_matches:
                    global current_target_width
                    
                    if len(text_matches) == 1:
                        # Single match - use it
                        match = text_matches[0]
                        print(f"Found single '{target_text}' at center coordinates: {match['coords']}")
                        current_target_width = match['width']
                        # Restore HUD command echo after OCR
                        if source_command:
                            restore_hud_command_echo(source_command)
                        actions.user.connect_ocr_eye_tracker()
                        return match['coords']
                    else:
                        # Sort by position for consistent ordering (top-to-bottom, left-to-right)
                        text_matches.sort(key=lambda m: (m['coords'][1], m['coords'][0]))
                        
                        # Multiple matches - pick closest to current cursor
                        print(f"Found {len(text_matches)} instances of '{target_text}' (sorted by position):")
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
                                # Restore HUD command echo after OCR
                                if source_command:
                                    restore_hud_command_echo(source_command)
                                actions.user.connect_ocr_eye_tracker()
                                return best_match['coords']
                        else:
                            # No cursor found, use first match
                            match = text_matches[0]
                            print(f"No cursor found, using first '{target_text}' at {match['coords']}")
                            current_target_width = match['width']
                            # Restore HUD command echo after OCR
                            if source_command:
                                restore_hud_command_echo(source_command)
                            actions.user.connect_ocr_eye_tracker()
                            return match['coords']
                
                print(f"Text '{target_text}' not found in OCR results")
            else:
                print("Could not find gaze_ocr_controller via any method")

            # Restore HUD command echo after OCR
            if source_command:
                restore_hud_command_echo(source_command)

            # Reconnect eye tracker
            actions.user.connect_ocr_eye_tracker()
            return None

        except Exception as e:
            print(f"Error getting text coordinates: {str(e)}")
            # Restore HUD command echo even on error
            if source_command:
                restore_hud_command_echo(source_command)
            actions.user.connect_ocr_eye_tracker()
            return None

    def check_if_disambiguation_needed(target_text: str, source_command: str = None) -> bool:
        """Check if multiple matches exist for the target text without doing full disambiguation"""
        try:
            # Disconnect eye tracker to scan full screen
            actions.user.disconnect_ocr_eye_tracker()

            # Clear HUD logs before OCR check
            if source_command:
                clear_hud_event_log()

            # Try different approaches to access the OCR controller
            import sys
            gaze_ocr_controller = None
            
            # Method 1: Check sys.modules for loaded gaze_ocr_talon
            for module_name, module in sys.modules.items():
                if 'gaze_ocr' in module_name and hasattr(module, 'gaze_ocr_controller'):
                    gaze_ocr_controller = module.gaze_ocr_controller
                    break
            
            if gaze_ocr_controller:
                # Trigger OCR scan without overlay
                gaze_ocr_controller.read_nearby()
                
                # Get the latest screen contents
                contents = gaze_ocr_controller.latest_screen_contents()
                
                # Count matches
                text_matches = []
                all_words = []
                
                for line_idx, line in enumerate(contents.result.lines):
                    for word_idx, word in enumerate(line.words):
                        # Store word for potential fuzzy matching
                        word_info = {
                            'coords': (word.left, word.top + word.height // 2),
                            'text': word.text,
                            'width': word.width,
                            'height': word.height,
                            'line': line_idx,
                            'word': word_idx
                        }
                        all_words.append(word_info)
                        
                        # Try exact matching first
                        if target_text.lower() in word.text.lower():
                            text_matches.append(word_info)
                
                # Check fuzzy matching if no exact matches
                if not text_matches and settings.get("user.menu_enable_fuzzy_matching") and RAPIDFUZZ_AVAILABLE and all_words:
                    fuzzy_threshold = settings.get("user.menu_fuzzy_threshold")

                    for word_info in all_words:
                        score = score_word_fuzzy(word_info['text'], target_text, fuzzy_threshold)
                        if score >= fuzzy_threshold:
                            text_matches.append(word_info)

                # Filter out results in the HUD log region
                if text_matches:
                    text_matches = filter_hud_log_results(text_matches)

                # Restore HUD command echo after OCR check
                if source_command:
                    restore_hud_command_echo(source_command)

                # Reconnect eye tracker
                actions.user.connect_ocr_eye_tracker()

                # Return True if more than one match
                result = len(text_matches) > 1
                print(f"Disambiguation check for '{target_text}': {len(text_matches)} matches found, needs_disambiguation={result}")
                return result
            else:
                print("Could not find gaze_ocr_controller for disambiguation check")
                # Restore HUD command echo even on failure
                if source_command:
                    restore_hud_command_echo(source_command)
                # Reconnect eye tracker
                actions.user.connect_ocr_eye_tracker()
                return False

        except Exception as e:
            print(f"Error checking disambiguation need: {str(e)}")
            # Restore HUD command echo even on error
            if source_command:
                restore_hud_command_echo(source_command)
            actions.user.connect_ocr_eye_tracker()
            return False

    def get_text_coordinates_generator(target_text: str, disambiguate: bool = True, source_command: str = None):
        """Generator version that yields multiple matches for disambiguation"""
        print(f"GENERATOR DEBUG: get_text_coordinates_generator called with target='{target_text}', disambiguate={disambiguate}")
        try:
            # Disconnect eye tracker to scan full screen
            actions.user.disconnect_ocr_eye_tracker()

            # Clear HUD logs before OCR scan
            if source_command:
                clear_hud_event_log()

            # Try different approaches to access the OCR controller
            import sys
            gaze_ocr_controller = None
            
            # Method 1: Check sys.modules for loaded gaze_ocr_talon
            for module_name, module in sys.modules.items():
                if 'gaze_ocr' in module_name and hasattr(module, 'gaze_ocr_controller'):
                    gaze_ocr_controller = module.gaze_ocr_controller
                    break
            
            if gaze_ocr_controller:
                # Trigger OCR scan without overlay
                gaze_ocr_controller.read_nearby()
                
                # Get the latest screen contents
                contents = gaze_ocr_controller.latest_screen_contents()
                
                # Search for the target text
                # PHASE 1: Try phrase sequence matching first (multi-word phrases)
                text_matches = []
                all_words = []
                
                # Check if this is a multi-word phrase
                target_words = target_text.split()
                if len(target_words) > 1:
                    print(f"Multi-word target detected: '{target_text}' -> {target_words}")
                    fuzzy_threshold = settings.get("user.menu_fuzzy_threshold", 0.8)
                    phrase_matches = find_phrase_sequences(target_text, contents.result.lines, fuzzy_threshold)
                    if phrase_matches:
                        # Sort phrase matches by score (best first)
                        phrase_matches.sort(key=lambda x: x['fuzzy_score'], reverse=True)
                        text_matches = phrase_matches
                        print(f"Found {len(text_matches)} phrase sequence matches for '{target_text}' (best score: {text_matches[0]['fuzzy_score']:.2f})")
                
                # PHASE 2: If no phrase matches, try individual word matching (original behavior)
                if not text_matches:
                    print(f"No phrase matches found, trying individual word matching for '{target_text}'")
                    
                    for line_idx, line in enumerate(contents.result.lines):
                        for word_idx, word in enumerate(line.words):
                            # Store word for potential fuzzy matching
                            word_info = {
                                'coords': (word.left, word.top + word.height // 2),
                                'text': word.text,
                                'width': word.width,
                                'height': word.height,
                                'line': line_idx,
                                'word': word_idx
                            }
                            all_words.append(word_info)
                            
                            # Try exact matching first
                            if target_text.lower() in word.text.lower():
                                text_matches.append(word_info)
                    
                    # If exact matches found, use them
                    if text_matches:
                        print(f"Found {len(text_matches)} exact word matches for '{target_text}'")
                    elif settings.get("user.menu_enable_fuzzy_matching") and RAPIDFUZZ_AVAILABLE and all_words:
                        # Try fuzzy matching as fallback
                        print(f"No exact matches for '{target_text}', trying fuzzy matching...")
                        fuzzy_threshold = settings.get("user.menu_fuzzy_threshold")
                        fuzzy_matches = []
                        
                        for word_info in all_words:
                            score = score_word_fuzzy(word_info['text'], target_text, fuzzy_threshold)
                            if score >= fuzzy_threshold:
                                word_info['fuzzy_score'] = score
                                fuzzy_matches.append(word_info)
                        
                        if fuzzy_matches:
                            # Sort by score (best first) and use fuzzy matches
                            fuzzy_matches.sort(key=lambda x: x['fuzzy_score'], reverse=True)
                            text_matches = fuzzy_matches
                            # Log the best score before any re-sorting
                            best_score = text_matches[0]['fuzzy_score'] if text_matches else 0
                            print(f"Found {len(text_matches)} fuzzy word matches for '{target_text}' (best score: {best_score:.2f})")

                # Filter out results in the HUD log region
                if text_matches:
                    text_matches = filter_hud_log_results(text_matches)

                if text_matches:
                    if len(text_matches) == 1:
                        # Single match - return coordinates directly
                        match = text_matches[0]
                        print(f"Found single '{target_text}' at center coordinates: {match['coords']}")
                        # Restore HUD command echo after OCR
                        if source_command:
                            restore_hud_command_echo(source_command)
                        actions.user.connect_ocr_eye_tracker()
                        return match['coords']
                    elif disambiguate:
                        # Sort by position for disambiguation (top-to-bottom, left-to-right)
                        text_matches.sort(key=lambda m: (m['coords'][1], m['coords'][0]))
                        
                        # Multiple matches - yield for disambiguation
                        print(f"Found {len(text_matches)} instances of '{target_text}', requiring disambiguation (sorted by position)")
                        for i, match in enumerate(text_matches):
                            print(f"  {i+1}. '{match['text']}' at {match['coords']}")
                        
                        # Yield matches and wait for user selection
                        chosen_match = yield text_matches
                        print(f"User chose match: '{chosen_match['text']}' at {chosen_match['coords']}")
                        print(f"SIMPLE_DEBUG: Coordinate fix starting now!")
                        
                        # CRITICAL FIX: The chosen_match contains NUMBER coordinates, not target word coordinates
                        # Find the actual target word closest to the selected number position
                        selected_number_coords = chosen_match['coords']
                        print(f"COORDINATE FIX: Selected number at {selected_number_coords}, finding closest '{target_text}' word")
                        
                        # Find closest target word to the selected number
                        closest_word = None
                        min_distance = float('inf')
                        
                        for match in text_matches:
                            # Calculate distance from number position to this word instance
                            word_coords = match['coords']
                            distance = actions.user.calculate_distance(selected_number_coords, word_coords)
                            print(f"  Distance from selected number {selected_number_coords} to '{match['text']}' at {word_coords}: {distance:.1f}px")
                            
                            if distance < min_distance:
                                min_distance = distance
                                closest_word = match
                        
                        if closest_word:
                            actual_target_coords = closest_word['coords']
                            print(f"COORDINATE FIX: Using closest word '{closest_word['text']}' at {actual_target_coords} (distance: {min_distance:.1f}px)")

                            # Trace the coordinate fix
                            from ..debug.coordinate_tracer import coord_tracer
                            coord_tracer.log_event('fixed', actual_target_coords, 'coordinate_fix', {
                                'original_number_coords': selected_number_coords,
                                'fixed_word_coords': actual_target_coords,
                                'word_text': closest_word['text'],
                                'distance': min_distance
                            })

                            # Restore HUD command echo after OCR
                            if source_command:
                                restore_hud_command_echo(source_command)

                            actions.user.connect_ocr_eye_tracker()
                            return actual_target_coords
                        else:
                            # Fallback to chosen match if something goes wrong
                            print("COORDINATE FIX: Warning - couldn't find closest word, using selected match")
                            # Restore HUD command echo after OCR
                            if source_command:
                                restore_hud_command_echo(source_command)
                            actions.user.connect_ocr_eye_tracker()
                            return chosen_match['coords']
                    else:
                        # Multiple matches but no disambiguation - use closest to cursor
                        cursor_pos = actions.user.find_cursor_flexible()
                        if cursor_pos:
                            best_match = None
                            min_distance = float('inf')
                            
                            for match in text_matches:
                                distance = actions.user.calculate_distance(cursor_pos, match['coords'])
                                if distance < min_distance:
                                    min_distance = distance
                                    best_match = match
                            
                            if best_match:
                                print(f"Selected closest '{target_text}' at {best_match['coords']} (distance: {min_distance:.1f}px)")
                                # Restore HUD command echo after OCR
                                if source_command:
                                    restore_hud_command_echo(source_command)
                                actions.user.connect_ocr_eye_tracker()
                                return best_match['coords']
                        else:
                            # No cursor found, use first match
                            match = text_matches[0]
                            print(f"No cursor found, using first '{target_text}' at {match['coords']}")
                            # Restore HUD command echo after OCR
                            if source_command:
                                restore_hud_command_echo(source_command)
                            actions.user.connect_ocr_eye_tracker()
                            return match['coords']
                
                print(f"Text '{target_text}' not found in OCR results")
            else:
                print("Could not find gaze_ocr_controller via any method")

            # Restore HUD command echo after OCR
            if source_command:
                restore_hud_command_echo(source_command)

            # Reconnect eye tracker
            actions.user.connect_ocr_eye_tracker()
            return None

        except Exception as e:
            print(f"Error getting text coordinates: {str(e)}")
            # Restore HUD command echo even on error
            if source_command:
                restore_hud_command_echo(source_command)
            actions.user.connect_ocr_eye_tracker()
            return None

    def check_if_disambiguation_needed(target_text: str, source_command: str = None) -> bool:
        """Check if multiple matches exist for the target text without doing full disambiguation"""
        try:
            # Disconnect eye tracker to scan full screen
            actions.user.disconnect_ocr_eye_tracker()

            # Clear HUD logs before OCR check
            if source_command:
                clear_hud_event_log()

            # Try different approaches to access the OCR controller
            import sys
            gaze_ocr_controller = None
            
            # Method 1: Check sys.modules for loaded gaze_ocr_talon
            for module_name, module in sys.modules.items():
                if 'gaze_ocr' in module_name and hasattr(module, 'gaze_ocr_controller'):
                    gaze_ocr_controller = module.gaze_ocr_controller
                    break
            
            if gaze_ocr_controller:
                # Trigger OCR scan without overlay
                gaze_ocr_controller.read_nearby()
                
                # Get the latest screen contents
                contents = gaze_ocr_controller.latest_screen_contents()
                
                # Count matches
                text_matches = []
                all_words = []
                
                for line_idx, line in enumerate(contents.result.lines):
                    for word_idx, word in enumerate(line.words):
                        # Store word for potential fuzzy matching
                        word_info = {
                            'coords': (word.left, word.top + word.height // 2),
                            'text': word.text,
                            'width': word.width,
                            'height': word.height,
                            'line': line_idx,
                            'word': word_idx
                        }
                        all_words.append(word_info)
                        
                        # Try exact matching first
                        if target_text.lower() in word.text.lower():
                            text_matches.append(word_info)
                
                # Check fuzzy matching if no exact matches
                if not text_matches and settings.get("user.menu_enable_fuzzy_matching") and RAPIDFUZZ_AVAILABLE and all_words:
                    fuzzy_threshold = settings.get("user.menu_fuzzy_threshold")

                    for word_info in all_words:
                        score = score_word_fuzzy(word_info['text'], target_text, fuzzy_threshold)
                        if score >= fuzzy_threshold:
                            text_matches.append(word_info)

                # Filter out results in the HUD log region
                if text_matches:
                    text_matches = filter_hud_log_results(text_matches)

                # Restore HUD command echo after OCR check
                if source_command:
                    restore_hud_command_echo(source_command)

                # Reconnect eye tracker
                actions.user.connect_ocr_eye_tracker()

                # Return True if more than one match
                result = len(text_matches) > 1
                print(f"Disambiguation check for '{target_text}': {len(text_matches)} matches found, needs_disambiguation={result}")
                return result
            else:
                print("Could not find gaze_ocr_controller for disambiguation check")
                # Restore HUD command echo even on failure
                if source_command:
                    restore_hud_command_echo(source_command)
                # Reconnect eye tracker
                actions.user.connect_ocr_eye_tracker()
                return False

        except Exception as e:
            print(f"Error checking disambiguation need: {str(e)}")
            # Restore HUD command echo even on error
            if source_command:
                restore_hud_command_echo(source_command)
            actions.user.connect_ocr_eye_tracker()
            return False