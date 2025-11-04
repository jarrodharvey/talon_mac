"""
Coordinate Provenance Tracking System
Tracks the lifecycle of coordinates through the pathfinding system
"""
import time
from typing import List, Dict, Any

class CoordinateTrace:
    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        
    def log_event(self, event_type: str, coordinates: tuple, source: str, extra_data: dict = None):
        """Log a coordinate event"""
        timestamp = time.time()
        event = {
            'timestamp': timestamp,
            'event_type': event_type,  # 'detected', 'cached', 'selected', 'used'
            'coordinates': coordinates,
            'source': source,  # function name or source description
            'extra_data': extra_data or {}
        }
        self.events.append(event)
        
        # Print immediate feedback
        print(f"COORD_TRACE: {event_type.upper()} {coordinates} from {source}")
        if extra_data:
            print(f"  Extra data: {extra_data}")
    
    def get_coordinate_history(self, coordinates: tuple) -> List[Dict[str, Any]]:
        """Get all events for specific coordinates"""
        return [event for event in self.events if event['coordinates'] == coordinates]
    
    def print_summary(self):
        """Print summary of all coordinate events"""
        print("=== COORDINATE TRACE SUMMARY ===")
        for i, event in enumerate(self.events):
            print(f"{i+1:2d}. {event['event_type'].upper():10} {event['coordinates']} from {event['source']}")
            if event['extra_data']:
                print(f"    {event['extra_data']}")
        print("================================")

# Global tracer instance
coord_tracer = CoordinateTrace()