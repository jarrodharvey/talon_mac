user.active_manual_game: ai the somnium files
mode: user.game
app: moonlight
-

settings():
    key_hold = 200
    user.centre_camera_method = "double_rmb"
    user.travel_distance = 2    

tag(): user.8bitdo_3d_staggered
tag(): user.wasd_directions_3d

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

# The lower the number the faster the speed of the staggered movement. Adjust to preference.
^walk$: user.set_global_variable("repeat_button_speed", 500)
^jog$: user.set_global_variable("repeat_button_speed", 200)
^sprint$: user.set_global_variable("repeat_button_speed", 250)
^tiptoe$: user.set_global_variable("repeat_button_speed", 800)