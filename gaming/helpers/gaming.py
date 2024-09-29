from talon import Module, actions, cron, storage, app, ctrl
import json
import time
import os

mod = Module()
mod.mode("game", desc="Mode for playing games")

mod.list("geforce_games", "Games that are supported by GeForce Now")
mod.list("cardinal_direction", "Match compass directions to arrows")

mod.tag("user_arrows", "Arrows for gaming")
mod.tag("cardinal_directions", "Cardinal directions")
mod.tag("boxes_gaming", "Used for boxes in gaming")

@mod.scope
def eye_tracker_active():
    if actions.tracking.control_enabled():
        return {"eye_tracker_active": "yes"}
    else:
        return {"eye_tracker_active": "no"}


travel_distance = 1

def str_to_bool(s):
    # Converts a string to a boolean. 
    # Assumes 'true', 'yes', '1' are True, and 'false', 'no', '0' are False.
    # Case-insensitive comparison.
    if s.lower() in ('true', 'yes', '1'):
        return True
    elif s.lower() in ('false', 'no', '0'):
        return False
    else:
        raise ValueError("Cannot convert string to boolean: " + s)

@mod.action_class
class Actions:
    def set_repeat_button(button: str, interval: float):
        """Populate button_interval.json with the button and interval"""
        # Define the path to the JSON file
        file_path = os.path.expanduser('~/.talon/user/jarrod/gaming/helpers/button_interval.json')
        
        # Create the data to be written to the file
        data = {
            "button": button,
            "interval": interval
        }
        
        # Write the data to the JSON file
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)

        print(f"Updated {file_path} with button: {button} and interval: {interval}") 
    def game_stop():
        """Stop gaming mode actions"""
        actions.key("left:up")
        actions.key("right:up")
        actions.key("up:up")
        actions.key("down:up")
        actions.key("u:up")
        actions.key("w:up")
        actions.key("a:up")
        actions.key("s:up")
        actions.key("d:up")
        actions.key("alt:up")
        actions.key("x:up")
        actions.key("tab:up")
        actions.user.stop_keypress()
        actions.user.hud_disable_id('Text panel')
        actions.user.flex_grid_boxes_toggle(0)
    def get_value_from_json_file(file_path: str, key: str) -> str:
        """Get the value of a key from a JSON file"""
        # Open the JSON file
        with open(file_path) as json_file:
            data = json.load(json_file)
        
        # Return the value of the key
        return data[key]
    def game_tracker_on():
        """Turns on the eye tracker"""
        actions.tracking.control_toggle(True)
        time.sleep(1)
        eye_tracker_active.update()
    def game_tracker_off(): 
        """Turns off the eye tracker"""
        actions.tracking.control_toggle(False)
        time.sleep(1)
        eye_tracker_active.update()
    def walk(arrow_dir: str):
        """Walk in a direction"""
        actions.key(f"{arrow_dir}")
        time.sleep(0.3)
    def diagonal(dir1: str, dir2: str, held_time: float = 0, hold: str = False):
        """Travel diagonally in a game"""
        hold = str_to_bool(hold)
        # The higher the hold_time_modifier, the faster the diagonal movement
        hold_time_modifier = 0.1 * travel_distance
        actions.user.game_stop()
        actions.key(f"{dir1}:down")
        actions.key(f"{dir2}:down")
        print("Held time: ", held_time)
        time.sleep(held_time * hold_time_modifier)
        if hold == False:
            actions.user.game_stop()
        return
    def super_click(duration: int = 0.05):
        """Click the mouse"""
        ctrl.mouse_click(button=0, down=True)
        time.sleep(duration)
        ctrl.mouse_click(button=0, up=True)
