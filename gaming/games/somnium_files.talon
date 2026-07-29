user.active_manual_game: ai the somnium files
mode: user.game
app: moonlight
-

settings():
    #key_hold = 200
    user.centre_camera_method = "double_rmb"
    user.travel_distance = 2    

tag(): user.8bitdo_wasd
tag(): user.wasd_directions_3d_staggered

parrot(click): 
    user.game_stop()
    key("enter")
parrot(tch): key("esc")

^<user.letters>$: key(letters)
^near$: key("a")

^stop$: user.game_stop()

^dialogue$: 
    key("c")
    user.set_single_press_button("c")
^gun$: user.set_single_press_button("ctrl")
^skip$: user.set_hold_button("ctrl")
^tutorial$: user.set_repeat_button("enter", 3)
^pages$: user.set_repeat_button("c", 9)

# Mashing buttons for QTEs
^mash escape$: user.set_repeat_button("esc", 0.08)
^mash tab$: user.set_repeat_button("tab", 0.08)
^mash space$: user.set_repeat_button("space", 0.08)

^(menu | present)$: key("tab")
^look$: key("space")

^<user.arrow_keys>$:
    key("{arrow_keys}:down")
    sleep(1)
    key("{arrow_keys}:up")

^raise$: 
    key("up:down")
    sleep(0.4)
    key("up:up")

^lower$: 
    key("down:down")
    sleep(0.4)
    key("down:up")

# The lower the number the faster the speed of the staggered movement. Adjust to preference.
^walk$: user.set_global_variable("repeat_button_speed", 500)
^jog$: user.set_global_variable("repeat_button_speed", 200)
^sprint$: user.set_global_variable("repeat_button_speed", 250)
^tiptoe$: user.set_global_variable("repeat_button_speed", 800)

key(`): 
    user.game_stop()
    key("space")

# Back
^quack$: user.press_key_x_times("escape", 4, 1) 

^save game$: 
    key("tab")
    sleep(500ms)
    user.click_image("somnium_save.png") 
    sleep(500ms)
    key("enter")
    sleep(500ms)
    user.click_image("somnium_yes.png") 
    sleep(500ms)
    user.betterinput_with_sleep("space | esc:2", "750ms")

^retry$: key("f2") 

^scan cursor$: user.start_cursor_scan()