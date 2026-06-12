user.active_manual_game: ai the somnium files
mode: user.game
app: moonlight
-

tag(): user.wasd_directions_3d
tag(): user.8bitdo_3d_movement

settings():
    user.centre_camera_method = "double_rmb"

parrot(click): key("enter")
parrot(tch): key("esc")

^stop$: user.game_stop()

^dialogue$: user.set_single_press_button("c")
^tutorial$: user.set_repeat_button("enter", 3)

^menu$: key("tab")
^whale$: key("w")
^air$: key("a")
^sun$: key("s")
^drum$: key("d")
^look$: key("space")

^<user.arrow_keys>$:
    key("{arrow_keys}:down")
    sleep(1)
    key("{arrow_keys}:up")

^(zoom | ray)$: key("q")