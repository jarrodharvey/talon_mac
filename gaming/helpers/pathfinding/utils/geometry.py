"""
Geometry and coordinate utility functions for pathfinding system.

Contains distance calculations, coordinate transformations, and geometric helpers.
"""

from talon import Module

mod = Module()

@mod.action_class  
class GeometryActions:
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
        
        # Create horizontal victory line extending left from text left edge
        line_x_start = text_left - left_extension  # Extend 50px left from text edge
        line_x_end = text_left
        line_y = text_center_y
        
        # Check if line intersects cursor rectangle
        # Line intersects horizontally if: line_x_start <= cursor_right AND line_x_end >= cursor_left
        line_intersects_horizontally = (line_x_start <= cursor_right and line_x_end >= cursor_left)
        
        # Line intersects vertically if: cursor_top <= line_y <= cursor_bottom
        line_intersects_vertically = (cursor_top <= line_y <= cursor_bottom)
        
        intersection = line_intersects_horizontally and line_intersects_vertically
        
        if intersection:
            print(f"VICTORY LINE: Cursor {cursor_pos} intersects victory line!")
            print(f"  Text: center={text_coords}, left_edge={text_left}, width={text_width}")
            print(f"  Cursor rect: ({cursor_left},{cursor_top}) to ({cursor_right},{cursor_bottom})")
            print(f"  Victory line: X({line_x_start} to {line_x_end}), Y={line_y}")
        else:
            print(f"Victory line: No intersection")
            print(f"  H-intersect: {line_intersects_horizontally} (line {line_x_start}-{line_x_end} vs cursor {cursor_left}-{cursor_right})")
            print(f"  V-intersect: {line_intersects_vertically} (line Y={line_y} vs cursor {cursor_top}-{cursor_bottom})")
        
        return intersection