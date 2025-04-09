user.active_manual_game: pokemon white
mode: user.game
app: moonlight
-
settings():
    key_hold = 30
    user.super_click_duration = 0.75

tag(): user.cardinal_directions
tag(): user.user_arrows
tag(): user.8bitdo_selite

parrot(click): 
    user.game_stop()
    key("x")
parrot(tch): 
    user.game_stop()
    key("z")

^start$: key("enter")
^menu$: 
    user.game_stop()
    key("s")
parrot(kiss): 
    user.game_stop()
    key("a")
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
    user.click_image("bw2_save.png") 
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
^triple$: user.press_key_x_times("x", 3, 1)

^track$: user.press_key_x_times("z", 3, 2)
^quack: user.press_key_x_times("z", 4, 2)

^(item | swimming)$: 
    user.game_stop()
    user.press_key_x_times("x", 3, 3)

^grinding$: user.start_grinding("x", 200, "pokemon_white_battle.png")

^trick$: 
    user.click_then_wait(1)
    repeat(2)

^inventory$: 
    user.game_stop()
    key("s")
    sleep(1s)
    user.click_image("bw2_bag.png") 
    sleep(1s)
    key("x")

^inventory$: 
    user.game_stop()
    key("s")
    sleep(1s)
    user.click_image("bw2_bag.png") 
    sleep(1s)
    key("x")

^pokemon$: 
    user.game_stop()
    key("s")
    sleep(1s)
    user.click_image("bw_pokemon.png") 
    sleep(1s)

^shift${"type":"response","action":{"type":"noAction"},"actions":[]}: user.click_image("pokemon_white_shift.png") 

^poke one$: user.click_spot("poke one")
^poke two$: user.click_spot("poke two")
^poke three$: user.click_spot("poke three")
^(poke for | perk full)$: user.click_spot("poke for")
^poke five$: user.click_spot("poke five")
^poke six$: user.click_spot("poke six")

^switch out$: user.click_spot("switch out")

^box left$: user.click_image("pk_box_left.png")
^box right$: user.click_image("pk_box_right.png")

^detail$: key("q")