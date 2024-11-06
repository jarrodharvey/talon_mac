user.active_manual_game: ace attorney investigations
mode: user.game
app: steamstreamingclient
app: moonlight
-

settings():
    key_hold = 70
    user.travel_distance = 3

tag(): user.cardinal_directions

{user.wasd_arrows}: key("{wasd_arrows}")

^stop$: user.game_stop()

parrot(click): key("space")
parrot(tch): 
    user.game_stop()
    key("z")

^mash$: user.set_repeat_button("space", 3)
^rapid$: user.set_repeat_button("space", 0.1)

^touch <user.timestamped_prose>$:
    user.click_text(timestamped_prose)
    user.super_click()

^run$: key("shift")
^(organizer | evidence)$: key("e")
^logic$: key("q")
^press$: key("q")
^partner$: key("t")
^present$: key("t")
^connect$: key("t")
^deduce$: key("t")
^options$: key("g")
^history$: key("r")

^spin <user.arrow_keys>$: user.start_keypress(arrow_keys, 1)
^zoom in$: key("q")
^zoom out$: key("e")

^save game$: 
    key("g")
    user.press_key_x_times("space", 4, 1)
    sleep(1s)
    key("w")
    sleep(1s)
    key("space")
    sleep(2s)
    user.press_key_x_times("z", 4, 1)

^mistake$:
    key("g")
    sleep(1s)
    user.click_spot("attorney load")
    user.press_key_x_times("space", 3, 1)

^examine$: user.click_image("aa_examine.png")
^chatter$: user.click_image("aa_chat.png")

^scroll$: user.press_key_x_times("down", 3, 0.5)

^scroll up$: user.press_key_x_times("up", 3, 0.5)

^quit moonlight$: 
    key("ctrl-alt-shift-q")

^puppy$: 
    user.click_spot("attorney yes")

^face tester$: user.face_tester_toggle()