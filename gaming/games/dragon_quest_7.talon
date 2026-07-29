user.active_manual_game: dragon quest 7
mode: user.game
app: moonlight
-

settings():
    key_hold = 200
    user.super_click_duration = 0.8
    user.travel_distance = 1

# Enable arrow key movement commands
tag(): user.8bitdo_wasd_diagonal
tag(): user.wasd_directions

# Parrot sounds for common actions - click sound triggers main action button
parrot(click): 
    user.game_stop()
    key("space")
# Tch sound for cancel/back actions
parrot(tch): 
    user.game_stop()
    key("backspace")

^stop$: user.game_stop()

^dialogue$: user.set_repeat_button("space", 5)
^magic$: 
    key("r")
    user.set_single_press_button("r")

^scroll down$: 
    key("k:down")
    sleep(0.4)
    key("k:up")
^scroll up$: 
    key("i:down")
    sleep(0.4)
    key("i:up")

^menu$: key("tab")

^knock [{user.number_small}]$: user.betterinput_with_sleep("e:{number_small or 1}", "200ms")
^previous [{user.number_small}]$: user.betterinput_with_sleep("q:{number_small or 1}", "200ms")