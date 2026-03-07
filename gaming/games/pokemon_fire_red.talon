user.active_manual_game: pokemon fire red
mode: user.game
app: mGBA
-

settings():
    key_hold = 70
    user.navigation_mode = "unified"
    user.cursor_directory = "fire_red"

tag(): user.8bitdo_selite

# mGBA button mappings:
# A: x
# B: z
# Start: enter
# Select: shift
# D-pad: arrow keys

parrot(click): key("x")
parrot(tch): key("z")

^dialogue$: user.set_repeat_button("x", 5)

key(`):
    user.conditional_image_button_press("x", "unbound_triangle.png", 2500, true, 0, true, "unbound_triangle.png")

