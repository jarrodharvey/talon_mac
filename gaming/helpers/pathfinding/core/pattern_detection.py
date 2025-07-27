"""
Pattern detection and loop prevention for pathfinding system.

Handles position tracking, loop detection, tiebreaker logic, and navigation stability.
"""

from talon import Module, actions, settings
import time

mod = Module()

# Global variables for pattern detection (shared with navigation system)
stable_position_history = []  # Track only stable/settled cursor positions
position_timing = {}  # Track when cursor first arrived at each position

@mod.action_class
class PatternDetectionActions:
    def add_position_if_stable(current_pos: tuple) -> None:
        """Add position to stable history only if cursor has been there long enough"""
        global stable_position_history, position_timing
        
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

    def get_stable_position_history() -> list:
        """Get current stable position history (for debugging/testing)"""
        global stable_position_history
        return stable_position_history.copy()

    def clear_position_tracking() -> None:
        """Clear all position tracking data (used when starting new navigation)"""
        global stable_position_history, position_timing
        stable_position_history = []
        position_timing = {}
        print("Cleared position tracking data")