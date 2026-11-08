user.active_manual_game: pokemon gold
mode: user.game
app: moonlight
-

settings():
    key_hold = 30
    user.super_click_duration = 0.25
    user.uses_wasd = false
    # Instant move+click over Moonlight sometimes lands before the host applies the cursor move
    user.ocr_click_delay = 150
    user.ocr_click_hold = 100

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
^slowly$: user.set_repeat_button("x", 5)

^walk$: user.set_global_variable("repeat_button_speed", 750)
^jog$: user.set_global_variable("repeat_button_speed", 500)
^sprint$: user.set_global_variable("repeat_button_speed", 250)
^tiptoe$: user.set_global_variable("repeat_button_speed", 1000)

^save game$: 
    user.game_stop()
    user.click_image("gold_save.png") 
    key("x")
    sleep(1s)
    key("x")
    sleep(10s)
    key("z")
    
^healing$: 
    user.game_stop()
    user.press_key_x_times("x", 4, 1)
    sleep(6s)
    user.press_key_x_times("z", 3, 1)

^continue$: 
    user.press_key_x_times("z", 2, 1)

^(double | dub)$: user.press_key_x_times("x", 2, 1)
^(triple | trip)$: user.press_key_x_times("x", 3, 1)

^track$: user.press_key_x_times("z", 3, 2)
^quack: user.press_key_x_times("z", 4, 2)

^(item | swimming)$: 
    user.game_stop()
    user.press_key_x_times("x", 3, 3)

^grinding$: user.start_grinding("x", 200, "pokemon_gold_battles.png")

^inventory$:
    user.game_stop()
    key("s")
    sleep(1s)
    user.click_image("bw2_bag.png")
    sleep(1s)
    key("x")

^pokemon$: 
    user.click_image("gold_pokemon.png") 

^shift$: user.click_image("pokemon_white_shift.png") 

^switch out$: user.click_image("gold_switch.png")

^box left$: user.click_image("pk_box_left.png")
^box right$: user.click_image("pk_box_right.png")

^tricky$: user.set_repeat_button("click", 1)

key(`):
    user.set_repeat_button("z", 3)
    user.conditional_image_button_press("z", "gold_chat.png", 2500, true, 1500, true, "x", "x")

^last$:
    user.click_image("gold_bag.png") 
    user.click_image("gold_last.png") 
    user.press_key_x_times("x", 2, 1)
    user.set_repeat_button("x", 5)

^running$: user.game_click_spot("running")

^learn set$: 
    user.click_image("gold_summary.png")
    user.click_image("gold_learnset.png")

^telephone$: 
    user.click_image("gold_gear.png")

^touch$: user.super_click()

^dang$: 
    user.game_stop()
    user.betterinput_with_sleep("down | x", "500ms")

^rang$: 
    user.game_stop()
    user.betterinput_with_sleep("right | x", "500ms")