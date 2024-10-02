mode: user.game
app: NVidia GeForce NOW
title: /disco elysium/i
user.boxes_gaming_status: off
-
settings():
    key_wait = 40
    mouse_wheel_down_amount = 500
tag(): user.user_arrows
tag(): user.cardinal_directions
^boxes$: user.boxes_gaming_status_on()

[left] (touch | click) <user.timestamped_prose>$:
    user.click_text(timestamped_prose)

^<number_small>$: key("{number_small}")

^stop$: user.game_stop()

back: key("escape")

face(brow_outer_up_left:start): key("tab:down")
face(brow_outer_up_left:stop): key("tab:up")

parrot(click): key("return")
parrot(tch): 
    user.game_stop()
    key("escape")

^character$:
    user.game_stop()
    key("c")
^inventory$: 
    key("i")
    sleep(1s)
^thinking$: 
    user.game_stop()
    key("t")
^(journal | channel)$:
    user.game_stop()
    key("j")
^help$: key("f1")
^map$: 
    user.game_stop()
    key("m")
quick save: key("f5")

^zoom out$: 
    user.mouse_scroll_down()
    repeat(100)
^zoom in$: 
    user.mouse_scroll_up()
    repeat(5)

^scroll$: 
    user.mouse_scroll_down()
    repeat(300)

^scroll up$: 
    user.mouse_scroll_up()
    repeat(300)

^(goat | dot)$: user.flex_grid_find_boxes() 
^go <number>$: 
    user.flex_grid_go_to_box(number or 1, -1)
    mouse_click()

^four$: key("4")

^calibrate eye tracker$: tracking.calibrate()