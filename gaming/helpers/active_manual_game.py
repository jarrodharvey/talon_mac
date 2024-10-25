# Set the game name manually when this can't be fetched by talon
from talon import Module, actions, cron, storage, app
import json
import time
import os

mod = Module()
mod.list("manual_games", "Games that need to be declared manually")

@mod.scope
def active_manual_game():
    return {"active_manual_game": storage.get("user.manual_game")}

@mod.action_class
class Actions:
    def set_manual_game(game: str):
        """Set the active manual Now game"""
        storage.set("user.manual_game", game)
        active_manual_game.update()
        print(f"Active manual game set to: {game}")
    def get_manual_game() -> str:
        """Get the active manual Now game"""
        game_title = storage.get("user.manual_game")
        app.notify(f"Active manual game: {game_title}")