from talon import actions, Module, settings, cron

mod = Module()

# Define settings for the buttons to be pressed, defaulting to None
mod.setting("wink_button_left", type=str, default="", desc="Button to press when winking left")
mod.setting("wink_button_right", type=str, default="", desc="Button to press when winking right")

class FacialExpressionDetector:
    def __init__(self):
        self.is_blinking = False
        self.wink_job = None
        self.wink_check_delay = 0.05  # 50 milliseconds

    def blink_start(self):
        self.is_blinking = True
        self.cancel_wink_job()

    def blink_stop(self):
        self.is_blinking = False
        self.reset()

    def left_eye_start(self):
        if not self.is_blinking:
            self.schedule_wink_check("left")

    def right_eye_start(self):
        if not self.is_blinking:
            self.schedule_wink_check("right")

    def schedule_wink_check(self, side):
        # Cancel any existing job to avoid conflicts
        if self.wink_job:
            cron.cancel(self.wink_job)
        # Schedule a check after the specified delay
        self.wink_job = cron.after(f"{int(self.wink_check_delay * 1000)}ms", lambda: self.process_wink(side))

    def process_wink(self, side):
        if not self.is_blinking:  # Double-check that a blink isn't in progress
            button = settings.get(f"user.wink_button_{side}")
            if button:  # Only press the button if it has been specified
                print(f"{side.capitalize()} wink detected - pressing {button}")
                actions.key(button)
        self.reset()

    def cancel_wink_job(self):
        if self.wink_job:
            cron.cancel(self.wink_job)
            self.wink_job = None

    def reset(self):
        self.is_blinking = False
        self.wink_job = None

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