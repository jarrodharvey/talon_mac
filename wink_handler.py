from talon import actions, Module, settings, cron

mod = Module()

# Define settings for the buttons to be pressed, defaulting to None
mod.setting("wink_button_left", type=str, default="", desc="Button to press when winking left")
mod.setting("wink_button_right", type=str, default="", desc="Button to press when winking right")
mod.setting("wink_cooldown", type=float, default=2, desc="Cooldown period after a wink to prevent rapid successive triggers (in seconds)")

class FacialExpressionDetector:
    def __init__(self):
        self.is_blinking = False
        self.wink_job = None
        self.cooldown_job = None
        self.is_in_cooldown = False
        self.wink_check_delay = 0.07  # 60 milliseconds

    def blink_start(self):
        self.is_blinking = True
        self.cancel_wink_job()

    def blink_stop(self):
        self.is_blinking = False
        self.reset()

    def left_eye_start(self):
        if not self.is_blinking and not self.is_in_cooldown:
            self.schedule_wink_check("left")

    def right_eye_start(self):
        if not self.is_blinking and not self.is_in_cooldown:
            self.schedule_wink_check("right")

    def schedule_wink_check(self, side):
        # Cancel any existing job to avoid conflicts
        if self.wink_job:
            cron.cancel(self.wink_job)
        # Schedule a check after the specified delay
        self.wink_job = cron.after(f"{int(self.wink_check_delay * 1000)}ms", lambda: self.process_wink(side))

    def process_wink(self, side):
        if not self.is_blinking and not self.is_in_cooldown:  # Double-check that a blink isn't in progress and not in cooldown
            button = settings.get(f"user.wink_button_{side}")
            # If the value of button is rmb, press the right mouse button
            if button == "rmb":
                actions.mouse_click(1)
            elif button:  # Only press the button if it has been specified and it's not "rmb"
                print(f"{side.capitalize()} wink detected - pressing {button}")
                actions.key(button)
            # Start cooldown immediately after processing the wink
            self.start_cooldown()

    def start_cooldown(self):
        # Start the cooldown period to prevent multiple triggers from the same wink
        self.is_in_cooldown = True
        cooldown_duration = settings.get("user.wink_cooldown")
        self.cooldown_job = cron.after(f"{int(cooldown_duration * 1000)}ms", self.end_cooldown)
        # Reset immediately after starting the cooldown
        self.reset()

    def end_cooldown(self):
        self.is_in_cooldown = False

    def cancel_wink_job(self):
        if self.wink_job:
            cron.cancel(self.wink_job)
            self.wink_job = None

    def reset(self):
        self.wink_job = None
        self.is_blinking = False

# Create an instance of the detector
detector = FacialExpressionDetector()

@mod.action_class
class Actions:
    def blink_start():
        """Handles the start of a blink."""
        detector.blink_start()

    def blink_stop():
        """Handles the stop of a blink."""
        detector.blink_stop()

    def left_eye_start():
        """Handles the start of left eye closing."""
        detector.left_eye_start()

    def right_eye_start():
        """Handles the start of right eye closing."""
        detector.right_eye_start()