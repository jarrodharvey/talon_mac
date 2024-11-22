from talon import Module, actions, cron, ctrl

stop_job = None
key_held = False

compensation_directions = {
    "right": "left",
    "left": "right",
    "up": "down",
    "down": "up"
}

mod = Module()

@mod.action_class
class Actions:
    def noise_start(key_to_hold: str):
        """noise start"""
        global stop_job, key_held
        if stop_job:
            cron.cancel(stop_job)
            stop_job = None
            return

        def hold_key():
            actions.key(f"{key_to_hold}:down")
            print(f"Holding key {key_to_hold}")
        
        hold_key()
        key_held = True
        stop_job = cron.interval("100ms", hold_key)  # Adjust the interval as needed

    def noise_stop(key_to_hold: str, cron_interval: int = 200, compensatory_steps: int = 0):
        """noise stop"""
        global stop_job, key_held
        if not key_held:
            return

        def do_stop():
            global stop_job, key_held
            actions.key(f"{key_to_hold}:up")
            print(f"Releasing key {key_to_hold}")
            if compensatory_steps > 0:
                compensation_direction = compensation_directions[key_to_hold]
                actions.user.press_key_x_times(compensation_direction, compensatory_steps, 0.5)
            stop_job = None
            key_held = False

        if stop_job:
            cron.cancel(stop_job)
        stop_job = cron.after(f"{cron_interval}ms", do_stop)