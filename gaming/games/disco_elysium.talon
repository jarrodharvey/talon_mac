mode: user.game
app: NVidia GeForce NOW
title: /disco elysium/i
user.boxes_gaming_status: off
-
settings():
    key_wait = 20
tag(): user.user_arrows
tag(): user.cardinal_directions
^boxes$: user.boxes_gaming_status_on()

[left] (touch | click) <user.timestamped_prose>$:
    user.click_text(timestamped_prose)

^<number_small>$: key("{number_small}")

^stop$: user.game_stop()

back: key("escape")
face(raise_eyebrows): key("tab:down")
face(raise_eyebrows:stop): key("tab:up")

face(pucker_lips_right): key("return")
face(pucker_lips_left): 
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
    repeat(5)
^zoom in$: 
    user.mouse_scroll_up()
    repeat(5)

^(goat | dot)$: user.flex_grid_find_boxes() 
^go <number>$: 
    user.flex_grid_go_to_box(number or 1, -1)
    mouse_click()