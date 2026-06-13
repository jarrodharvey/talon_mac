tag: user.8bitdo_3d_staggered
mode: user.game
-

# Bindings for the 8bitdo selite controller in 3D games via hid-remapper.
# Each direction key starts a slow, staggered cron-driven nudge. Speed is
# governed by the repeat_button_speed global. Designed for RSI-friendly
# step-at-a-time movement in 3D worlds.

# Cardinal directions (orient + centre camera, then stagger forward)
key(keypad_4:down): user.diagonal_3d("a", "a", "yes")
key(keypad_6:down): user.diagonal_3d("d", "d", "yes")
key(keypad_8:down): user.diagonal_3d("w", "w", "yes")
key(keypad_2:down): user.diagonal_3d("s", "s", "yes")

# Forward diagonal movement
key(;): user.diagonal_3d("w", "a")
key([): user.diagonal_3d("w", "d")

# Single-direction staggered movement (no camera centring)
key(pageup:down): user.repeat_button_with_cron("w")
key(pagedown:down): user.repeat_button_with_cron("s")
key(home:down): user.repeat_button_with_cron("a")
key(end:down): user.repeat_button_with_cron("d")
