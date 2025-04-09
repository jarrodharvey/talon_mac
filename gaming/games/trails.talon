user.active_manual_game: trails in the sky
mode: user.game
app: moonlight
-

settings():
    key_hold = 30
    user.super_click_duration = 1.5
    user.travel_distance = 1
tag(): user.cardinal_directions
tag(): user.user_arrows
tag(): user.8bitdo_diagonal

parrot(click): 
    user.game_stop()
    key("space")
parrot(tch): 
    user.game_stop()
    key("ctrl")

^eyebrows$: user.eyebrow_toggle()

face(brow_outer_up_left:start): user.press_key_if_condition_met("z:down", "brow_rotate", "yes")
face(brow_outer_up_left:stop): key("z:up")

face(brow_down_right:start): user.press_key_if_condition_met("x:down", "brow_rotate", "yes")
face(brow_down_right:stop): key("x:up")

^walk$: user.set_global_variable("repeat_button_speed", "750")
^jog$: user.set_global_variable("repeat_button_speed", 500)
^sprint$: user.set_global_variable("repeat_button_speed", 250)
^tiptoe$: user.set_global_variable("repeat_button_speed", 1000)

^dialogue$: user.set_repeat_button("space", 5)
^speed$: user.set_repeat_button("space", 0.5)
^advance$: user.set_repeat_button("space", 2)