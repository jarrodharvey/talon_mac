mode: user.game
tag: user.8bitdo_wasd_actual_diagonal
-

# Bindings for the 8bitdo selite controller, passed through hid-remapper.
# Used for WASD movement with diagonal control

key(;): user.game_stop()

# Keypad for straight line movement
key(keypad_4): user.repeat_diagonal_with_cron("a", "s")
key(keypad_6): user.repeat_diagonal_with_cron("w", "d")
key(keypad_8): user.repeat_diagonal_with_cron("w", "a")
key(keypad_2): user.repeat_diagonal_with_cron("s", "d")

# Other keys for diagonal movement
key(pageup:down): user.stop_and_press_key("w")
key(pagedown:down): user.stop_and_press_key("s")
key(home:down): user.stop_and_press_key("a")
key(end:down): user.stop_and_press_key("d")