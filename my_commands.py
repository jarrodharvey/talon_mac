import talon
from talon import Context, Module, actions, app, fs, imgui, ui

mod = Module()

@mod.action_class
class Actions:
    def dictation_mode():
        """Enable dictation mode"""
        actions.mode.disable("sleep")
        actions.mode.disable("command")
        actions.mode.disable("user.game")
        actions.mode.enable("dictation")
        actions.user.code_clear_language_mode()
        actions.user.gdb_disable()
    def command_mode():
        """Enable command mode"""
        actions.mode.disable("sleep")
        actions.mode.disable("dictation")
        actions.mode.disable("user.game")
        actions.mode.enable("command")
    def game_mode():
        """Enable game mode"""
        actions.mode.disable("sleep")
        actions.mode.disable("dictation")
        actions.mode.disable("command")
        actions.mode.enable("user.game")
    def join_spaces(my_list: list) -> str:
        """Joins a list of strings with spaces"""
        return " ".join(my_list)


