mode: user.game
tag: user.8bitdo_diagonal
-

# Bindings for the 8bitdo selite controller, passed through hid-remapper.
# Used primarily for directional pad control

key(;): user.game_stop()

# Up on numpad
key(keypad_8): user.repeat_diagonal_with_cron("up", "right")
# Right on numpad
key(keypad_6): user.repeat_diagonal_with_cron("down", "right")
# Left on numpad
key(keypad_4): user.repeat_diagonal_with_cron("up", "left")
# Down on numpad
key(keypad_2): user.repeat_diagonal_with_cron("down", "left")

key(pageup:down): user.repeat_diagonal_with_cron("up", "up")
key(pagedown:down): user.repeat_diagonal_with_cron("down", "down")
key(home:down): user.repeat_diagonal_with_cron("left", "left")
key(end:down): user.repeat_diagonal_with_cron("right", "right")