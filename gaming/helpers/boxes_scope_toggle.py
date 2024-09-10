from talon import Module, actions, cron, storage, app
import json
import time
import os

mod = Module()

@mod.scope
def boxes_gaming_status():
    return {"boxes_gaming_status": storage.get("user.boxes_gaming_status")}

@mod.action_class
class Actions:
    def boxes_gaming_status_off():
        """Turn off gaming boxes"""
        actions.user.flex_grid_boxes_toggle(0)
        storage.set("user.boxes_gaming_status", "off")
        boxes_gaming_status.update()
        print(f"Box status set to: off")
    def boxes_gaming_status_on():
        """Turn on gaming boxes"""
        actions.user.flex_grid_find_boxes()
        storage.set("user.boxes_gaming_status", "on")
        boxes_gaming_status.update()
        print(f"Box status set to: on")