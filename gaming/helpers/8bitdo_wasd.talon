mode: user.game
tag: user.8bitdo_wasd
-

# Bindings for the 8bitdo selite controller, passed through hid-remapper.
# Used primarily for directional pad control

key(;): user.game_stop()

key(keypad_4): user.repeat_button_with_cron("a")
key(keypad_6): user.repeat_button_with_cron("d")
key(keypad_8): user.repeat_button_with_cron("w")
key(keypad_2): user.repeat_button_with_cron("s")

key(pageup:down): user.stop_and_press_key("w")
key(pagedown:down): user.stop_and_press_key("s")
key(home:down): user.stop_and_press_key("a")
key(end:down): user.stop_and_press_key("d")