from talon import Module, actions, cron, ctrl

stop_job = None
key_held = False
mod = Module()

@mod.action_class
class Actions:
    def noise_start(key_to_hold: str):
        """noise start"""
        global stop_job, key_held
        print(f"noise_start called, key_held: {key_held}, stop_job: {stop_job}")
        if stop_job:
            cron.cancel(stop_job)
            stop_job = None
            return

        def hold_key():
            actions.key(f"{key_to_hold}:down")
            print(f"noise_start, holding key {key_to_hold}")
        
        hold_key()
        key_held = True
        stop_job = cron.interval("100ms", hold_key)  # Adjust the interval as needed
        print(f"Started cron job with id: {stop_job}, key_held: {key_held}")

    def noise_stop(key_to_hold: str):
        """noise stop"""
        global stop_job, key_held
        print(f"noise_stop called, key_held: {key_held}, stop_job: {stop_job}")
        if not key_held:
            return

        def do_stop():
            global stop_job, key_held
            actions.key(f"{key_to_hold}:up")
            print(f"noise_stop, releasing key {key_to_hold}")
            stop_job = None
            key_held = False

        if stop_job:
            print(f"Cancelling cron job with id: {stop_job}")
            cron.cancel(stop_job)
        stop_job = cron.after("200ms", do_stop)
        print(f"Scheduled stop job with id: {stop_job}, key_held: {key_held}")