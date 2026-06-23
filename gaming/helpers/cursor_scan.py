from talon import Module, actions, app, cron, ctrl, settings, ui


mod = Module()

mod.setting(
    "cursor_scan_speed",
    type=int,
    default=600,
    desc="Cursor scan speed in pixels per second",
)

mod.setting(
    "cursor_scan_sample_spacing",
    type=int,
    default=5,
    desc="Horizontal distance in pixels between cursor scan hover samples",
)

mod.setting(
    "cursor_scan_row_spacing",
    type=int,
    default=10,
    desc="Vertical distance in pixels between cursor scan rows",
)


cursor_scan_job = None
cursor_scan_state = None


def stop_cursor_scan():
    global cursor_scan_job
    global cursor_scan_state

    if cursor_scan_job is not None:
        cron.cancel(cursor_scan_job)
        cursor_scan_job = None
    cursor_scan_state = None


def advance_cursor_scan():
    global cursor_scan_state

    if cursor_scan_state is None:
        return

    state = cursor_scan_state
    target_x = state["right"] if state["direction"] > 0 else state["left"]
    next_x = state["x"] + state["direction"] * state["sample_spacing"]

    if (state["direction"] > 0 and next_x >= target_x) or (
        state["direction"] < 0 and next_x <= target_x
    ):
        state["x"] = target_x
        ctrl.mouse_move(state["x"], state["y"])

        if state["y"] == state["bottom"]:
            stop_cursor_scan()
            app.notify("Cursor scan complete")
            return

        state["y"] = min(state["y"] + state["row_spacing"], state["bottom"])
        state["direction"] *= -1
    else:
        state["x"] = next_x

    ctrl.mouse_move(state["x"], state["y"])


@mod.action_class
class Actions:
    def start_cursor_scan(speed: int = 0):
        """Scan the main monitor from top-left in alternating horizontal rows.

        Speed is pixels per second. A value of zero uses user.cursor_scan_speed.
        """
        global cursor_scan_job
        global cursor_scan_state

        actions.user.game_stop()

        scan_speed = speed or settings.get("user.cursor_scan_speed")
        sample_spacing = settings.get("user.cursor_scan_sample_spacing")
        row_spacing = settings.get("user.cursor_scan_row_spacing")
        if scan_speed <= 0 or sample_spacing <= 0 or row_spacing <= 0:
            app.notify("Cursor scan settings must be greater than zero")
            return

        rect = ui.main_screen().rect
        left = int(rect.x)
        top = int(rect.y)
        right = int(rect.x + rect.width - 1)
        bottom = int(rect.y + rect.height - 1)

        cursor_scan_state = {
            "left": left,
            "right": right,
            "bottom": bottom,
            "x": left,
            "y": top,
            "direction": 1,
            "sample_spacing": sample_spacing,
            "row_spacing": row_spacing,
        }
        ctrl.mouse_move(left, top)

        interval_ms = max(1, round(1000 * sample_spacing / scan_speed))
        cursor_scan_job = cron.interval(f"{interval_ms}ms", advance_cursor_scan)

    def stop_cursor_scan():
        """Stop an active full-monitor cursor scan."""
        stop_cursor_scan()
