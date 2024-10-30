from talon import Module, actions, cron, storage, app, ctrl, settings
import json
import time
import os
import subprocess
import sys

# Global variables
mouth_open = "no"
mouse_dragging = "no"

images_to_click_location = "/Users/jarrod/.talon/user/jarrod/gaming/images_to_click/"

mod = Module()
mod.mode("game", desc="Mode for playing games")

mod.list("geforce_games", "Games that are supported by GeForce Now")
mod.list("cardinal_direction", "Match compass directions to arrows")
mod.list("wasd_arrows", "Arrows for the wasd movement letters")

mod.tag("user_arrows", "Arrows for gaming")
mod.tag("cardinal_directions", "Cardinal directions")
mod.tag("boxes_gaming", "Used for boxes in gaming")

mod.setting(
    "travel_distance",
    type=int,
    default=7,
    desc="Controls the speed at which a character moves in a game"
)

@mod.scope
def eye_tracker_active():
    if actions.tracking.control_enabled():
        return {"eye_tracker_active": "yes"}
    else:
        return {"eye_tracker_active": "no"}

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
        actions.key("q:up")
        actions.key("e:up")
        actions.key("alt:up")
        actions.key("x:up")
        actions.key("tab:up")
        actions.user.stop_keypress()
        actions.user.set_global_variable("mouth_open", "no")
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
        #time.sleep(1)
        eye_tracker_active.update()
    def game_tracker_off(): 
        """Turns off the eye tracker"""
        actions.tracking.control_toggle(False)
        #time.sleep(1)
        eye_tracker_active.update()
    def eye_tracker_on():
        """Turns on the eye tracker"""
        actions.tracking.control_toggle(True)
    def eye_tracker_off(): 
        """Turns off the eye tracker"""
        actions.tracking.control_toggle(False)
    def walk(arrow_dir: str):
        """Walk in a direction"""
        actions.key(f"{arrow_dir}")
        time.sleep(0.3)
    def diagonal(dir1: str, dir2: str, held_time: float = 0, hold: str = False):
        """Travel diagonally in a game"""
        hold = str_to_bool(hold)
        # The higher the hold_time_modifier, the faster the diagonal movement
        hold_time_modifier = 0.1 * settings.get("user.travel_distance")
        actions.user.game_stop()
        actions.key(f"{dir1}:down")
        actions.key(f"{dir2}:down")
        print("Held time: ", held_time)
        time.sleep(held_time * hold_time_modifier)
        if hold == False:
            actions.user.game_stop()
        return
    def super_click(duration: float = 0.05):
        """Click the mouse"""
        ctrl.mouse_click(button=0, down=True)
        time.sleep(duration)
        ctrl.mouse_click(button=0, up=True)
    def mouse_button_down(button: int):
        """Press down a mouse button"""
        if (mouse_dragging == "no"):
            actions.user.super_click()
        else:
            ctrl.mouse_click(button=button, down=True)
    def mouse_button_up(button: int):   
        """Release a mouse button"""
        ctrl.mouse_click(button=button, up=True)
    def click_image(image_name: str):
        """Clicks on an image and notifies if the click fails."""
        try:
            # Assuming actions.user.mouse_helper_move_image_relative throws an exception if the image is not found
            actions.user.mouse_helper_move_image_relative(images_to_click_location + image_name)
            time.sleep(1)
            actions.user.super_click()  # Assumes a click with button index 0
            time.sleep(1)
        except Exception as e:
            # Notify the user that the image could not be found or clicked
            app.notify(f"Failed to click the image: {image_name}. Error: {str(e)}")
    def set_global_variable(var_name: str, value: str):
        """Set a global variable"""
        globals()[var_name] = value
    def press_key_if_condition_met(key: str, condition: str, requirement: str):
        """Press a key if a condition is met"""
        if globals()[condition] == requirement:
            actions.key(key)
    def set_input_volume(volume: int):
        """
        Sets the input volume on macOS. For gaming with discord and talon.
        
        :param volume: An integer representing the desired input volume (0-100).
        """
        if not 0 <= volume <= 100:
            print("Volume must be between 0 and 100.")
            return
        
        try:
            subprocess.run(['osascript', '-e', f"set volume input volume {volume}"], check=True)
            print(f"Input volume set to {volume}%.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to set input volume. Error: {e}")

    if __name__ == "__main__":
        if len(sys.argv) != 2:
            print("Usage: python3 set_input_volume.py <volume>")
            sys.exit(1)
        
        try:
            volume = int(sys.argv[1])
            set_input_volume(volume)
        except ValueError:
            print("Please provide a valid integer for the volume.")
            sys.exit(1)
    def switch_microphone(mic_name: str) -> None:
        """
        Switches the audio input source to the specified microphone using SwitchAudioSource.
        
        Args:
            mic_name (str): The name of the microphone to switch to.
        """
        try:
            # Get the list of available audio input sources
            result = subprocess.run(
                ['SwitchAudioSource', '-a', '-t', 'input'], 
                capture_output=True, text=True, check=True
            )
            
            # Check if the specified microphone is in the list
            available_mics = result.stdout.splitlines()
            if mic_name not in available_mics:
                print(f"Microphone '{mic_name}' not found. Available microphones are:")
                for mic in available_mics:
                    print(f"- {mic}")
                return
            
            # Switch to the specified microphone
            subprocess.run(
                ['SwitchAudioSource', '-s', mic_name, '-t', 'input'], 
                check=True
            )
            print(f"Switched to '{mic_name}' microphone.")
        
        except subprocess.CalledProcessError as e:
            print(f"Error switching microphone: {e}")
    def press_key_x_times(key: str, times: int, interval: float):
        """Press a key a specified number of times with a specified interval"""
        for i in range(times):
            actions.key(key)
            time.sleep(interval)