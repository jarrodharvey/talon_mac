mode: user.game
app: moonlight
user.active_manual_game: mutazione
-

settings():
    key_hold = 30
    user.travel_distance = 5
    user.ocr_release_advance_image = "mutazione_chat.png"

tag(): user.8bitdo_wasd_diagonal
tag(): user.user_arrows
tag(): user.cardinal_directions

parrot(click): 
    user.game_stop()
    key("return")

parrot(tch): 
    user.game_stop()
    key("esc")

^dialogue$: user.set_repeat_button("return", 5)

# The larger the number the slower the speed of the staggered movement. Adjust to preference.
^walk$: user.set_global_variable("repeat_button_speed", 250)
^tiptoe$: user.set_global_variable("repeat_button_speed", 450)

key(`): 
    user.set_repeat_button("return", 4)
    user.conditional_image_button_press("return", "mutazione_chat.png", 5000, true, 0, true, "return")

^menu$: 
    user.game_stop()
    key("esc")

^go$: key("e")
^previous$: key("q")