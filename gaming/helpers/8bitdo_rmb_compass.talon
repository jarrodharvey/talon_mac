mode: user.game
tag: user.8bitdo_rmb_compass
-

# Bindings for the 8bitdo selite controller, passed through hid-remapper.
# Same control style as 8bitdo_selite.talon (used by pokemon_fire_red), but
# each tick drives RMB compass movement for right-click-to-move games like
# Wasteland 3. Walk speed is controlled by repeat_button_speed (cron
# interval) and user.travel_distance (per-tick RMB hold duration).

key(;): user.game_stop()

# Numpad cardinals -> compass directions
# 8 = north (cursor center-top), 2 = south, 4 = west, 6 = east
key(keypad_8): user.repeat_diagonal_with_cron("up", "up", true)
key(keypad_2): user.repeat_diagonal_with_cron("down", "down", true)
key(keypad_4): user.repeat_diagonal_with_cron("left", "left", true)
key(keypad_6): user.repeat_diagonal_with_cron("right", "right", true)
