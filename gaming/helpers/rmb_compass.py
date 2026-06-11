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

mod.setting(
    "rmb_camera_follow_ratio",
    type=float,
    default=0.5,
    desc="Fraction of each RMB burst (0.0-1.0) to hold camera-follow arrow keys. Lower = less camera pan per walking step. 0 disables camera follow."
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
    def rmb_compass_move(direction: str, held_time: float = 0, clear_other: bool = True, camera_keys: list = None):
        """Hold RMB at compass screen position; held_time=0 holds until rmb_compass_stop().
        clear_other=True (default) calls game_stop() first to release any other held keys.
        Pass clear_other=False when calling from inside a cron tick to avoid cancelling
        the cron itself (game_stop cancels button_presser_job).
        camera_keys: optional list of arrow keys to hold for user.rmb_camera_follow_ratio
        of the RMB burst, then release before RMB releases (camera-follow for games where
        the camera doesn't track short RMB bursts on its own, e.g. Wasteland 3)."""
        global rmb_held
        if direction not in COMPASS_POSITIONS:
            return
        if clear_other:
            actions.user.game_stop()
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
            if camera_keys:
                ratio = max(0.0, min(1.0, settings.get("user.rmb_camera_follow_ratio")))
                camera_sleep = sleep_time * ratio
                if camera_sleep > 0:
                    for k in camera_keys:
                        actions.key(f"{k}:down")
                    time.sleep(camera_sleep)
                    for k in camera_keys:
                        actions.key(f"{k}:up")
                remainder = sleep_time - camera_sleep
                if remainder > 0:
                    time.sleep(remainder)
            else:
                time.sleep(sleep_time)
            actions.user.rmb_compass_stop()

    def rmb_compass_stop():
        """Release RMB if currently held by compass movement"""
        global rmb_held
        if rmb_held:
            ctrl.mouse_click(button=1, up=True)
            rmb_held = False
