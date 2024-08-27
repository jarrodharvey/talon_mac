from talon import Module, actions
import json
import os

mod = Module()
mod.mode("game", desc="Mode for playing games")

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
        actions.user.stop_keypress()
        actions.user.hud_disable_id('Text panel')
    def get_value_from_json_file(file_path: str, key: str) -> str:
        """Get the value of a key from a JSON file"""
        # Open the JSON file
        with open(file_path) as json_file:
            data = json.load(json_file)
        
        # Return the value of the key
        return data[key]
