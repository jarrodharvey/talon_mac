from talon import Module, actions, cron, storage, app
import json
import time
import os

mod = Module()

@mod.scope
def active_geforce_game():
    return {"active_geforce_game": storage.get("user.geforce_game")}

@mod.action_class
class Actions:
    def set_geforce_game(game: str):
        """Set the active GeForce Now game"""
        storage.set("user.geforce_game", game)
        active_geforce_game.update()
        print(f"Active GeForce Now game set to: {game}")
    def get_geforce_game() -> str:
        """Get the active GeForce Now game"""
        game_title = storage.get("user.geforce_game")
        app.notify(f"Active GeForce Now game: {game_title}")