# bg3_map_movement.py

from talon import Module, Context, actions, ctrl, app
from math import cos, sin, radians
import time  # Required for smoother dragging

mod = Module()
ctx = Context()

# Define the list of directions and their corresponding angles
directions_dict = {
    "up": 90,
    "down": 270,
    "right": 0,
    "left": 180,
}

mod.list("direction", desc="Directions for map movement")
ctx.lists["user.direction"] = directions_dict.keys()

@mod.action_class
class Actions:
    def move_map(direction: str, times: int):
        """Move the map in a given direction a specific number of times"""
        if times is None:
            times = 1
        angle = directions_dict.get(direction.lower())
        if angle is None:
            app.notify(f"Unknown direction: {direction}")
            return
        for _ in range(times):
            actions.user.drag_in_direction(angle)
            actions.sleep("150ms")  # Adjust delay between drags if needed

    def drag_in_direction(angle: float):
        """Hold left mouse button and drag mouse in a specific angle smoothly"""
        distance = 200  # Adjust as needed
        steps = 20      # Number of steps for the movement
        delay = 0.01    # Delay between steps in seconds

        dx_total = cos(radians(angle)) * distance
        dy_total = sin(radians(angle)) * distance

        dx_step = dx_total / steps
        dy_step = dy_total / steps
        x_start, y_start = ctrl.mouse_pos()
        x, y = x_start, y_start

        ctrl.mouse_click(button=0, down=True)
        for _ in range(steps):
            x -= dx_step  # Invert X movement
            y += dy_step  # Y movement remains the same
            ctrl.mouse_move(x, y)
            time.sleep(delay)
        ctrl.mouse_click(button=0, up=True)
        # Return mouse to original position
        ctrl.mouse_move(x_start, y_start)