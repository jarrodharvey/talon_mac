from talon import Module, actions, cron, storage, app, ctrl, settings

mod = Module()

@mod.scope
def hiss_dpad_active():
    return {"hiss_dpad_active": storage.get("user.hiss_dpad_active")}

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