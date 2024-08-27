mode: user.game
-
settings():
    key_wait = 5

^command mode$:
    mode.disable("user.game")
    mode.enable("command")