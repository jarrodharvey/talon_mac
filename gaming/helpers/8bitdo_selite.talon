mode: user.game
tag: user.8bitdo_selite
-

# Bindings for the 8bitdo selite controller, passed through hid-remapper.
# Used primarily for directional pad control

key(;): user.game_stop()

key(keypad_4): user.repeat_button_with_cron("left")
key(keypad_6): user.repeat_button_with_cron("right")
key(keypad_8): user.repeat_button_with_cron("up")
key(keypad_2): user.repeat_button_with_cron("down")

key(pageup:down): user.stop_and_press_key("up")
key(pagedown:down): user.stop_and_press_key("down")
key(home:down): user.stop_and_press_key("left")
key(end:down): user.stop_and_press_key("right")