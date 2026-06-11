user.active_manual_game: wasteland 3
mode: user.game
app: moonlight
-

settings():
    user.game_action_button = "enter"
    user.default_action_button_interval = 1
    user.travel_distance = 4
    user.rmb_camera_follow_ratio = 0.5

tag(): user.rmb_compass_directions
tag(): user.8bitdo_rmb_compass
tag(): user.user_arrows

^<user.arrow_keys> [<number>]$: user.diagonal(arrow_keys, arrow_keys, 1 or number, "False") 

parrot(click):
    user.game_stop()
    mouse_click(1)

parrot(tch):
    user.game_stop()
    key("escape")

^bang$: key("return")

^move$: mouse_click(1)

face(brow_outer_up_left:start): key("shift:down")
face(brow_outer_up_left:stop): key("shift:up")

^scroll [{user.number_small}]$:
    repeat_times = user.simple_math("{number_small or 1} * 80")
    user.mouse_scroll_up()
    repeat(repeat_times)

^scroll up [{user.number_small}]$:
    repeat_times = user.simple_math("{number_small or 1} * 80")
    user.mouse_scroll_down()
    repeat(repeat_times)

^touch$: user.super_click()

^stop$: user.game_stop()

# Camera (INSERT→keypad_0, DELETE→fn-delete, HOME→fn-home on Mac via Moonlight)
^snap$: key("fn-home")
^zoom$:
    key("keypad_0:down")
    sleep(500ms)
    key("keypad_0:up")
^zoom out$:
    key("fn-delete:down")
    sleep(500ms)
    key("fn-delete:up")

# End turn / group mode
^turn$: key("space")

# Save / load
^quick save$: key("f5")
^quick load$: key("f9")

# Dialogue advancement
^dialogue$: user.set_repeat_button("click", 5)

# Images
^loot$: 
    user.click_image("wasteland_loot.png") 
    user.set_repeat_button("click", 3)

# Back
^dack$: user.betterinput_with_sleep("esc:2", "500ms")
^track$: user.betterinput_with_sleep("esc:3", "500ms")
^quack$: user.betterinput_with_sleep("esc:4", "500ms")

# Battle menu
^attack$: key(1)
^reload$: key(2)
^stand$: key(3)
^ability$: key(4)
^item$: key(5)

# Battle final actions
^ambush$: key("v")
^defend$: key("b")
^prepare$: key("n")

# Field
^inventory$: key("i")

^switch$: key("tab")