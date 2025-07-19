user.active_manual_game: chained echoes
mode: user.game
app: moonlight
-

settings():
    #key_hold = 30
    user.super_click_duration = 0.8
    user.travel_distance = 1
    user.navigation_mode = "vertical"
    user.game_action_button = "space" 
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
    key("escape")

# Kiss sound toggles eyebrow-based directional controls
parrot(kiss): 
    user.game_stop()
    user.eyebrow_toggle()

# Movement speed controls for exploration
^walk$: user.set_global_variable("repeat_button_speed", 750)
^jog$: user.set_global_variable("repeat_button_speed", 500)
^sprint$: user.set_global_variable("repeat_button_speed", 250)
^tiptoe$: user.set_global_variable("repeat_button_speed", 1000)

^action$: key("space")
^confirm$: key("space")
^cancel$: key("escape")
^back$: key("escape")

^menu$: key("i")
^inventory$: key("i")
^pause$: key("p")

^quick save$: key("f5")
^quick load$: key("f9")

# Speed up battle animations
^battle speed$: key("tab")
^fast$: key("tab")

# Combat system commands - overdrive management is key to Chained Echoes
^overdrive$: key("o")
^guard$: key("g")
^defend$: key("g")

# Flee from battle
^run$: key("r")
^escape$: key("r")
^flee$: key("r")

# Target selection in combat
^target next$: key("right")
^target previous$: key("left")
^next target$: key("right")
^previous target$: key("left")

# Party member selection (F1-F4 for 4-person party)
^party one$: key("f1")
^party two$: key("f2")
^party three$: key("f3")
^party four$: key("f4")

^first$: key("f1")
^second$: key("f2")
^third$: key("f3")
^fourth$: key("f4")

# Automated dialogue advancement with different speeds
^tutorial$: user.set_repeat_button("space", 5)
^dialogue$: user.set_repeat_button("space", 2.5)

^stop$: user.game_stop()

# Rapid button mashing for dialogue skip
^mash$: user.set_repeat_button("space", 0.5)
^careful$: user.set_repeat_button("space", 2)

^world map$: key("m")
^map$: key("m")

^options$: key("o")
^settings$: key("o")

^double$: user.press_key_x_times("space", 2, 1)

# Dynamic menu navigation - navigate to any word using OCR
^go <user.word>$: user.navigate_to_word_wasd_with_action(word)

^quack: user.press_key_x_times("escape", 4, 2)