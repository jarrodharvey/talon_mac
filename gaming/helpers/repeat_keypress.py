import time
from talon import Module, actions, cron

mod = Module()
keypress_job = None

def press_key(key_to_press: str, hold_ms: int = 0):
    if key_to_press == "click":
        actions.user.super_click()
    elif hold_ms > 0:
        actions.key(f"{key_to_press}:down")
        time.sleep(hold_ms / 1000)
        actions.key(f"{key_to_press}:up")
    else:
        actions.key(key_to_press)

@mod.action_class
class Actions:
    def start_keypress(key_to_press: str, interval: float, hold_ms: int = 0):
        """Start pressing the specified key at the given interval"""
        global keypress_job
        actions.user.game_stop()  # Ensure no other keypress jobs are active
        press_key(key_to_press, hold_ms)
        interval_ms = f"{int(interval * 1000)}ms"
        keypress_job = cron.interval(interval_ms, lambda: press_key(key_to_press, hold_ms))

    def stop_keypress(key_to_press: str = "x", final_press: bool = False):
        """Stop pressing the specified key"""
        global keypress_job
        if keypress_job:
            cron.cancel(keypress_job)
            keypress_job = None
        if final_press:
            actions.key(key_to_press)
