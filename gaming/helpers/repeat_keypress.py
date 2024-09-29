import time
import threading
from talon import Module, actions

mod = Module()
keypress_thread = None
keep_pressing = False

def press_key(key_to_press: str, interval: float):
    while keep_pressing:
        actions.key(f"{key_to_press}:down")
        time.sleep(0.1)
        actions.key(f"{key_to_press}:up")
        time.sleep(interval)

@mod.action_class
class Actions:
    def start_keypress(key_to_press: str, interval: float):
        """Start pressing the specified key at the given interval"""
        global keypress_thread, keep_pressing
        actions.user.game_stop()  # Ensure no other keypress threads are active
        keep_pressing = True
        if keypress_thread is None or not keypress_thread.is_alive():
            keypress_thread = threading.Thread(target=press_key, args=(key_to_press, interval))
            keypress_thread.start()

    def stop_keypress(key_to_press: str = "x", final_press: bool = False):
        """Stop pressing the specified key"""
        global keep_pressing
        keep_pressing = False
        if final_press:
            actions.key(key_to_press)