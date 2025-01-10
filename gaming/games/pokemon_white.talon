user.active_manual_game: pokemon white
mode: user.game
app: moonlight
-
settings():
    key_hold = 30

tag(): user.cardinal_directions
tag(): user.user_arrows
tag(): user.8bitdo_selite

parrot(click): 
    user.game_stop()
    key("x")
bang$: key("x")
parrot(tch): 
    user.game_stop()
    key("z")

^start$: key("enter")
^menu$: 
    user.game_stop()
    key("s")
^map$: key("a")
^detail$: key("q:down")

^dialogue$: user.set_repeat_button("z", 3)
^speed$: user.set_repeat_button("x", 0.5)
^advance$: user.set_repeat_button("x", 2)

^walk$: user.set_global_variable("repeat_button_speed", 750)
^jog$: user.set_global_variable("repeat_button_speed", 500)
^sprint$: user.set_global_variable("repeat_button_speed", 250)
^tiptoe$: user.set_global_variable("repeat_button_speed", 1000)

^save game$: 
    user.game_stop()
    sleep(500ms)
    key("s")
    sleep(1s)
    user.click_image("bw_save.png") 
    sleep(2500ms)
    key("x")
    sleep(1s)
    key("x")
    sleep(10s)
    key("z")

^healing$: 
    user.game_stop()
    user.set_repeat_button("z", 1)
    user.press_key_x_times("x", 4, 2)

^continue$: 
    user.press_key_x_times("z", 2, 1)

^double$: user.press_key_x_times("x", 2, 1)
^(item | surf)$: 
    user.game_stop()
    user.press_key_x_times("x", 3, 3)
^bang$: user.press_key_x_times("x", 2, 0.5)

^grinding$: user.start_grinding("x", 200, "pokemon_white_battle.png")