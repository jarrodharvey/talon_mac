user.active_manual_game: pokemon white
mode: user.game
app: moonlight
-

settings():
    key_hold = 30

tag(): user.cardinal_directions
tag(): user.user_arrows

parrot(click): key("x")
bang$: key("x")
parrot(tch): key("z")

^start$: key("enter")
^menu$: key("s")

^dialogue$: user.set_repeat_button("z", 3)
^speed$: user.set_repeat_button("x", 0.5)
^advance$: user.set_repeat_button("x", 2)

^save game$: 
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

^double$: user.press_key_x_times("x", 2, 1)

key(;): user.game_stop()