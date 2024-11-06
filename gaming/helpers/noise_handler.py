from talon import Module, actions, cron, ctrl

stop_job = None
mod = Module()

@mod.action_class
class Actions:
    def noise_start(key_to_hold: str):
        """whistle_start"""
        if stop_job:
            cron.cancel(stop_job)
            return

        actions.key(f"{key_to_hold}:down")
        print(f"noise_start, holding key {key_to_hold}")

    def noise_stop(key_to_hold: str):
        """whistle_stop"""
        def do_stop():
            global stop_job
            actions.key(f"{key_to_hold}:up")
            print(f"noise_stop, holding key {key_to_hold}")
            stop_job = None
        global stop_job
        if stop_job:
            cron.cancel(stop_job)
        stop_job = cron.after("200ms", do_stop) 