from talon import Module, actions, cron, storage, app, ctrl, settings, noise
import time

mod = Module()

@mod.scope
def hiss_dpad_active():
    return {"hiss_dpad_active": storage.get("user.hiss_dpad_active")}

mod.setting(
    "noise_step_interval",
    type=int,
    default=0.2,
    desc="Controls the speed at which a character moves in a game"
)

mod.setting(
    "action_button",
    type=str,
    default="space",
    desc="The action button for a game"
)

@mod.action_class
class Actions:
    def hiss_dpad_on():
        """Turns on the hissing directional pad"""
        storage.set("user.hiss_dpad_active", "yes")
        hiss_dpad_active.update()
        print(f"hiss dpad on")
    def hiss_dpad_off():
        """Turns off the hissing directional pad"""
        storage.set("user.hiss_dpad_active", "no")
        hiss_dpad_active.update()
        print(f"hiss dpad off")
    def take_step(direction: str):
        """Take a step in the given direction"""
        actions.user.game_stop()
        actions.key(f"{direction}:down")
        time.sleep(settings.get("user.noise_step_interval"))
        actions.key(f"{direction}:up")
    def press_action_button():
        """Press the action button"""
        actions.key(f"{settings.get('user.action_button')}:down")
        time.sleep(settings.get("user.noise_step_interval"))
        actions.key(f"{settings.get('user.action_button')}:up")