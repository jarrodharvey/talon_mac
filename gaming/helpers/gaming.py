from talon import Module, actions, cron, storage, app, ctrl, settings, scope, Context
import json
import time
import os
import subprocess
import sys
import random
from datetime import date

# Global variables
mouth_open = "no"
mouse_dragging = "no"
cron_left_eye_closed = None
cron_right_eye_closed = None
brow_direction = None 
button_presser_job = None
grinding_job = None
conditional_image_job = None
conditional_image_delay_job = None
repeat_button_speed = 250
brow_rotate = "no"
mouse_mover_job = None
looking_around = "no"

images_to_click_location = "/Users/jarrod/.talon/user/jarrod/gaming/images_to_click/"

ctx = Context()
ctx.matches = "mode: user.game"

mod = Module()
mod.mode("game", desc="Mode for playing games")

mod.list("geforce_games", "Games that are supported by GeForce Now")
mod.list("cardinal_direction", "Match compass directions to arrows")
mod.list("wasd_arrows", "Arrows for the wasd movement letters")

mod.tag("user_arrows", "Arrows for gaming")
mod.tag("cardinal_directions", "Cardinal directions")
mod.tag("wasd_directions", "Cardinal directions")
mod.tag("wasd_directions_3d", "Cardinal directions")
mod.tag("boxes_gaming", "Used for boxes in gaming")
mod.tag("ocr_click_button", "Used for holding down a button that enables clicking on dictated text")
mod.tag("ocr_pathfinding_button", "Used for holding down a button that enables pathfinding navigation to dictated text")
mod.tag("8bitdo_selite", "Used for 8bitdo selite controller")
mod.tag("8bitdo_wasd", "Used for 8bitdo selite controller")
mod.tag("8bitdo_wasd_diagonal", "Used for 8bitdo selite controller")
mod.tag("8bitdo_diagonal", "Used for 8bitdo selite controller")
mod.tag("8bitdo_3d_movement", "Used for 8bitdo selite controller")
mod.tag("pathfinding_cubes", "Tag for games that support cubes pathfinding navigation")

mod.setting(
    "travel_distance",
    type=int,
    default=7,
    desc="Controls the speed at which a character moves in a game"
)


mod.setting(
    "forward_button",
    type=str,
    default="w",
    desc="The forward button in a video game"
)

mod.setting(
    "centre_camera_button",
    type=str,
    default="w",
    desc="The centre camera in a video game"
)

mod.setting(
    "mouse_movement_speed",
    type=int,
    default=1000,
    desc="Controls the speed at which the mouse moves"
)

mod.setting(
    "mouse_movement_distance",
    type=int,
    default=1000,
    desc="Controls the distance at which the mouse moves"
)

mod.setting(
    "super_click_duration",
    type=int,
    default=0.5,
    desc="Duration of a super click"
)

mod.setting(
    "uses_pathfinding",
    type=bool,
    default=False,
    desc="Use pathfinding navigation instead of mouse clicking for OCR button"
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
        global button_presser_job
        global grinding_job
        global mouse_mover_job
        global conditional_image_job
        global conditional_image_delay_job

        actions.key("left:up")
        actions.key("right:up")
        actions.key("up:up")
        actions.key("down:up")
        actions.key("u:up")
        actions.key("z:up")
        actions.key("x:up")
        actions.key("w:up")
        actions.key("a:up")
        actions.key("s:up")
        actions.key("d:up")
        actions.key("q:up")
        actions.key("0:up")
        actions.key("e:up")
        actions.key("alt:up")
        actions.key("x:up")
        actions.key("tab:up")
        actions.key("ctrl:up")
        actions.user.stop_keypress()
        actions.user.set_global_variable("mouth_open", "no")
        actions.user.set_global_variable("brow_rotate", "no")
        actions.user.hud_disable_id('Text panel')
        actions.user.flex_grid_boxes_toggle(0)
        actions.user.noise_stop("right")
        actions.user.noise_stop("left")
        actions.user.noise_stop("up")
        actions.user.noise_stop("down")
        actions.user.stop_left_eye_closed_cron("left")
        actions.user.stop_right_eye_closed_cron("right")
        cron.cancel(mouse_mover_job)
        mouse_mover_job = None
        cron.cancel(button_presser_job)
        button_presser_job = None
        cron.cancel(grinding_job)
        grinding_job = None
        cron.cancel(conditional_image_job)
        conditional_image_job = None
        cron.cancel(conditional_image_delay_job)
        conditional_image_delay_job = None
        actions.user.stop_continuous_navigation()
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
    def diagonal(dir1: str, dir2: str, held_time: float = 0, hold: str = False, stop_self: bool = True):
        """Travel diagonally in a game"""
        print(f"DIAGONAL START: {dir1}, {dir2}, held_time={held_time}, hold={hold}, stop_self={stop_self}")
        if stop_self:
            # Check if gamepad movement was active before calling game_stop
            gamepad_was_active = button_presser_job is not None
            print(f"DIAGONAL: gamepad_was_active={gamepad_was_active}")
            actions.user.game_stop()
            
            # Only add delay when transitioning FROM gamepad movement
            if gamepad_was_active:
                time.sleep(0.15)  # 150ms buffer for gamepad→voice transition (was 50ms)
                print("Gamepad→voice transition: added 150ms stabilization delay")
        hold = str_to_bool(hold)
        # The higher the hold_time_modifier, the faster the diagonal movement
        hold_time_modifier = 0.1 * settings.get("user.travel_distance")
        print(f"DIAGONAL: pressing {dir1}:down and {dir2}:down")
        actions.key(f"{dir1}:down")
        actions.key(f"{dir2}:down")
        sleep_time = held_time * hold_time_modifier
        print(f"DIAGONAL: sleeping for {sleep_time} seconds")
        time.sleep(sleep_time)
        if hold == False and stop_self:
            print("DIAGONAL: calling game_stop() because hold=False and stop_self=True")
            actions.user.game_stop()
        if stop_self == False:
            print(f"DIAGONAL: releasing {dir1}:up and {dir2}:up")
            actions.key(f"{dir1}:up")
            actions.key(f"{dir2}:up")
        print("DIAGONAL END")
        return
    def conditional_click():
        """Super click if the mouse is not dragging,  otherwise button down"""
        if mouse_dragging == "no":
            actions.user.super_click()
        else:
            actions.user.mouse_button_down(0)
    def super_click():
        """Click the mouse"""
        ctrl.mouse_click(button=0, down=True)
        time.sleep(settings.get("user.super_click_duration"))
        ctrl.mouse_click(button=0, up=True)
    def mouse_button_down(button: int):
        """Press down a mouse button"""
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
    def noise_step(key_to_hold: str, interval: float):
        """Hold a key for a specified interval"""
        actions.user.noise_start(key_to_hold)
        time.sleep(interval)
        actions.user.noise_stop(key_to_hold)
    def start_left_eye_closed_cron(eye_closed_key: str):
        """Starts a cron job to check if the eye is closed"""
        global cron_left_eye_closed
        cron_left_eye_closed = cron.after("500ms", lambda: actions.key(f"{eye_closed_key}:down"))
    def stop_left_eye_closed_cron(eye_closed_key: str):
        """Stops the cron job to check if the eye is closed"""
        global cron_left_eye_closed
        cron.cancel(cron_left_eye_closed)
        actions.key(f"{eye_closed_key}:up")
    def start_right_eye_closed_cron(eye_closed_key: str):
        """Starts a cron job to check if the eye is closed"""
        global cron_right_eye_closed
        cron_right_eye_closed = cron.after("500ms", lambda: actions.key(f"{eye_closed_key}:down"))
    def stop_right_eye_closed_cron(eye_closed_key: str):
        """Stops the cron job to check if the eye is closed"""
        global cron_right_eye_closed
        cron.cancel(cron_right_eye_closed)
        actions.key(f"{eye_closed_key}:up")
    def brow_kiss():
        """Kiss with the brow"""
        if brow_direction == "up":
            actions.key("left")
        elif brow_direction == "down":
            actions.key("right")
    def brow_raspberry():
        """Raspberry with the brow"""
        if brow_direction == "up":
            actions.key("up")
        elif brow_direction == "down":
            actions.key("down")
    def gamepad_east_down():
        """Actions taken when the east button on the gamepad is pressed"""
        if scope.get("user.hiss_dpad_active") == "yes":
            actions.key("right:down")
        else:
            button_to_press = actions.user.get_value_from_json_file("/Users/jarrod/.talon/user/jarrod/gaming/helpers/button_interval.json", "button")
            interval_in_seconds = actions.user.get_value_from_json_file("/Users/jarrod/.talon/user/jarrod/gaming/helpers/button_interval.json", "interval")
            actions.user.start_keypress(button_to_press, interval_in_seconds)
            actions.user.hud_publish_content(f'Pressing {button_to_press} every {interval_in_seconds} seconds', 'example', 'Pressing button')
    def daily_exercise_reminder():
        """Reminds me to do daily exercises"""
        date_last_called = storage.get("user.date_last_called")
        today = str(date.today())
        if date_last_called != today:
            app.notify("Remember to FEMDAC if you haven't already today.")
            storage.set("user.date_last_called", today)
        else:
            print("No need for exercise reminder today.")
    def enable_ocr_click_button():
        """Enables OCR click or pathfinding based on game settings"""
        actions.user.game_stop()
        actions.user.disconnect_ocr_eye_tracker()
        
        # Check if current game uses pathfinding instead of mouse clicking
        if settings.get("user.uses_pathfinding"):
            # Add pathfinding tag to existing context instead of replacing
            current_tags = list(ctx.tags) if ctx.tags else []
            print(f"DEBUG: Before adding pathfinding tag - current tags: {current_tags}")
            print(f"DEBUG: Current disambiguation color setting: {settings.get('user.disambiguation_number_color', 'NOT_SET')}")
            if "user.ocr_pathfinding_button" not in current_tags:
                current_tags.append("user.ocr_pathfinding_button")
            ctx.tags = current_tags
            print(f"DEBUG: After adding pathfinding tag - new tags: {current_tags}")
            print("Enabled pathfinding mode for OCR navigation")
        else:
            # Add click tag to existing context instead of replacing  
            current_tags = list(ctx.tags) if ctx.tags else []
            if "user.ocr_click_button" not in current_tags:
                current_tags.append("user.ocr_click_button")
            ctx.tags = current_tags
            print("Enabled mouse click mode for OCR navigation")
    
    def disable_ocr_click_button():
        """Disables both OCR click and pathfinding modes"""
        actions.user.connect_ocr_eye_tracker()
        # Remove only the OCR tags, keep other existing tags
        current_tags = list(ctx.tags) if ctx.tags else []
        current_tags = [tag for tag in current_tags if tag not in ["user.ocr_pathfinding_button", "user.ocr_click_button"]]
        ctx.tags = current_tags
        print("Disabled OCR navigation mode")
    def game_click_spot(phrase: str):
        """Clicks a spot on the screen"""
        actions.user.move_to_spot(phrase)
        time.sleep(0.5)
        actions.user.super_click()
    def release_all_arrow_keys_except_one(arrow_key: str):
        """Releases all arrow keys except one"""
        arrow_keys = ["left", "right", "up", "down"]
        for key in arrow_keys:
            if key != arrow_key:
                actions.key(f"{key}:up")
    def repeat_button_with_cron(button: str):
        """Repeats a button press with a cron job"""
        global button_presser_job, repeat_button_speed
        actions.user.game_stop()
        button_presser_job = cron.interval(f"{repeat_button_speed}ms", lambda: actions.key(button))
    def repeat_diagonal_with_cron(button1: str, button2: str):
        """Repeats two button presses simultaneously with a cron job"""
        global button_presser_job, repeat_button_speed
        actions.user.game_stop()
        button_presser_job = cron.interval(f"{repeat_button_speed}ms", lambda: actions.user.diagonal(button1, button2, 1, "False", False))
    def stop_and_press_key(key: str):
        """Stops all actions and presses a key"""
        actions.user.game_stop()
        cron.after("10ms", lambda: actions.key(key))
    def image_appeared_on_screen(image: str):
        """Detects if an image appears on screen"""
        # returns true with a specific image of piece on the screen.
        image_coordinates = actions.user.mouse_helper_find_template_relative(f"{images_to_click_location}{image}")
        return(len(image_coordinates) > 0)
    def start_grinding(action_button: str, interval: int, battle_image: str):
        """Start grinding in a game"""
        global grinding_job
        actions.user.game_stop()
        grinding_job = cron.interval(f"{interval}ms", lambda: actions.user.grinding(action_button, battle_image))
    def grinding(action_button: str, battle_image: str):
        """If the battle image is on the screen then press the action button, otherwise press a random direction button"""
        directions = ["left", "right", "up", "down"]
        if actions.user.image_appeared_on_screen(battle_image):
            actions.key(action_button)
        else:
            actions.key(directions[random.randint(0,3)])
    def conditional_image_button_press(action_button: str, image_name: str, wait_time: int = 0, image_present: bool = True, wait_before: int = 0, stop_first: bool = True, initial_button: str = "", press_final_button: str = ""):
        """Presses a button if an image is present or not present on the screen"""
        global conditional_image_job
        global conditional_image_delay_job
        if stop_first:
            actions.user.game_stop()

        def start_conditional_check():
            global conditional_image_job
            if image_present:
                conditional_image_job = cron.interval(f"{wait_time}ms", lambda: actions.user.conditional_image_button_press_helper(action_button, image_name, True, press_final_button))
            else:
                conditional_image_job = cron.interval(f"{wait_time}ms", lambda: actions.user.conditional_image_button_press_helper(action_button, image_name, False, press_final_button))

        if initial_button:
            # Press initial button asynchronously after game_stop settles
            cron.after("50ms", lambda: actions.key(initial_button))

        if wait_before > 0:
            conditional_image_delay_job = cron.after(f"{wait_before}ms", start_conditional_check)
        else:
            start_conditional_check()
    def conditional_image_button_press_helper(action_button: str, image_name: str, image_present: bool, press_final_button: str = ""):
        """Helper function for conditional image button press"""
        global conditional_image_job
        # Check if the image is present on the screen
        # If it is, press the action button, otherwise cancel the cron job
        image_found = actions.user.image_appeared_on_screen(image_name)
        if image_found == image_present:
            actions.key(action_button)
        else:
            # Schedule both cancel and final press outside this callback context
            def cleanup_and_final():
                global conditional_image_job
                cron.cancel(conditional_image_job)
                conditional_image_job = None
                if press_final_button:
                    time.sleep(0.5)  # Wait for game to be ready
                    actions.key(press_final_button)
            cron.after("10ms", cleanup_and_final)
    def click_then_wait(wait_time: int):
        """Clicks the mouse then waits for a specified time"""
        actions.user.super_click()
        time.sleep(wait_time)
    def double_click_then_wait(wait_time: int):
        """Double clicks the mouse then waits for a specified time"""
        actions.user.super_click(0.01)
        actions.user.super_click(0.01)
        actions.user.super_click(0.01)
        time.sleep(wait_time)
    def eyebrow_toggle():
        """Toggles the eyebrow"""
        global brow_rotate
        if brow_rotate == "no":
            actions.user.set_global_variable("brow_rotate", "yes")
        else:
            actions.user.set_global_variable("brow_rotate", "no")
        actions.user.hud_publish_content(f'Toggled eyebrow rotation to {brow_rotate}', 'example', 'Eyebrow rotation')
    def divide_by_forty_five(number: int):
        """Divides a number by 45"""
        if number == 0:
            return 0
        else:
            return number / 45
    def multi_keypress(key_to_press: str, interval: int, times: float):
        """Presses a key multiple times"""
        for i in range(int(times)):
            actions.key(key_to_press)
            time.sleep(interval)
    def move_mouse_relative(direction: str, movement_distance: int = None):
        """moves the mouse relative to the current position"""
        if movement_distance is None:
            movement_distance = settings.get("user.mouse_movement_distance")
        if direction == "up":
            ctrl.mouse_move(ctrl.mouse_pos()[0], ctrl.mouse_pos()[1] - movement_distance)
        elif direction == "right":
            ctrl.mouse_move(ctrl.mouse_pos()[0] + movement_distance, ctrl.mouse_pos()[1])
        elif direction == "down":
            ctrl.mouse_move(ctrl.mouse_pos()[0], ctrl.mouse_pos()[1] + movement_distance)
        elif direction == "left":
            ctrl.mouse_move(ctrl.mouse_pos()[0] - movement_distance, ctrl.mouse_pos()[1])
    def relative_mouse_mover(direction: str):
        """Moves the mouse on a scheduled interval"""
        actions.user.game_stop()
        global mouse_mover_job 
        mouse_movement_speed = settings.get("user.mouse_movement_speed")
        mouse_movement_distance = settings.get("user.mouse_movement_distance")
        mouse_mover_job = cron.interval(f"{mouse_movement_speed}ms", lambda: actions.user.move_mouse_relative(direction))
    def diagonal_3d(dir1: str, dir2: str):
        """Travel diagonally in a 3d game"""
        actions.user.game_stop()
        centre_camera_button = settings.get("user.centre_camera_button")
        forward_button = settings.get("user.forward_button")
        current_game = storage.get("user.manual_game")
        time.sleep(0.2)
        actions.key(f"{dir1}:down")
        actions.key(f"{dir2}:down")
        time.sleep(0.2)
        actions.key(f"{dir1}:up")
        actions.key(f"{dir2}:up")
        time.sleep(0.2)
        actions.key("c")
        time.sleep(0.2)
        if looking_around == "no":
            actions.key(f"{forward_button}:down")
    def betterinput_simple(action_str: str):
        """Simple wrapper for betterinput with no bindings or options"""
        actions.user.betterinput(action_str, "", {})   
