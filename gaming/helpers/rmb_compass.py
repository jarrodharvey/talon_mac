from talon import Module, actions, ctrl, ui, settings
import time

mod = Module()
mod.tag("rmb_compass_directions", "RMB-based compass movement for right-click-to-move games")

mod.setting(
    "compass_margin",
    type=int,
    default=100,
    desc="Pixel inset from screen edge for RMB compass cursor positioning"
)

# (x_factor, y_factor): 0.0=left/top edge+margin, 1.0=right/bottom edge-margin, 0.5=center
COMPASS_POSITIONS = {
    "north":     (0.5, 0.0),
    "south":     (0.5, 1.0),
    "east":      (1.0, 0.5),
    "west":      (0.0, 0.5),
    "northeast": (1.0, 0.0),
    "northwest": (0.0, 0.0),
    "southeast": (1.0, 1.0),
    "southwest": (0.0, 1.0),
}

rmb_held = False

@mod.action_class
class Actions:
    def rmb_compass_move(direction: str, held_time: float = 0):
        """Hold RMB at compass screen position; held_time=0 holds until rmb_compass_stop()"""
        global rmb_held
        if direction not in COMPASS_POSITIONS:
            return
        screen = ui.main_screen()
        margin = settings.get("user.compass_margin")
        x_factor, y_factor = COMPASS_POSITIONS[direction]
        x = int(margin + (screen.width  - 2 * margin) * x_factor)
        y = int(margin + (screen.height - 2 * margin) * y_factor)
        actions.user.rmb_compass_stop()
        ctrl.mouse_move(x, y)
        ctrl.mouse_click(button=1, down=True)
        rmb_held = True
        if held_time > 0:
            sleep_time = held_time * 0.1 * settings.get("user.travel_distance")
            time.sleep(sleep_time)
            actions.user.rmb_compass_stop()

    def rmb_compass_stop():
        """Release RMB if currently held by compass movement"""
        global rmb_held
        if rmb_held:
            ctrl.mouse_click(button=1, up=True)
            rmb_held = False
