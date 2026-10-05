user.active_manual_game: dragon quest 7
mode: user.game
app: moonlight
-

# IMPORTANT NOTE REGARDING MOUSE CLICKS:
# Mouse click events in this game will not be received by moonlight unless a physical mouse is plugged into the host

settings():
    user.super_click_duration = 0.8
    user.ocr_click_delay = 200
    user.ocr_click_hold = 800
    key_hold = 10
    user.disable_hud_log_exclusion = 1
    user.travel_distance = 2

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

^dialogue$: user.set_repeat_button("backspace", 3)
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

^menu$: 
    user.game_stop() 
    key("tab")

^knock [{user.number_small}]$: user.betterinput_with_sleep("e:{number_small or 1}", "200ms")
^previous [{user.number_small}]$: user.betterinput_with_sleep("q:{number_small or 1}", "200ms")

# Movement speed controls for exploration
^walk$: user.set_global_variable("repeat_button_speed", 900)
^jog$: user.set_global_variable("repeat_button_speed", 500)
^sprint$: user.set_global_variable("repeat_button_speed", 250)
^tiptoe$: user.set_global_variable("repeat_button_speed", 1200)

^quack$: user.betterinput_with_sleep("backspace:4", "500ms")

key(`): 
    user.set_repeat_button("space", 2)
    user.conditional_image_button_press("space", "dragon_quest_chat.png", 3000, true, 0, true, "space", "space")

^left [{user.number_small}]$: user.hold_key_x_times("l", "{number_small or 1}", 500, 0.5)
^right [{user.number_small}]$: user.hold_key_x_times("j", "{number_small or 1}", 500, 0.5)