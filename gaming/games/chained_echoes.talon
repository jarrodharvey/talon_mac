user.active_manual_game: chained echoes
mode: user.game
app: moonlight
-

settings():
    user.super_click_duration = 0.8
    user.travel_distance = 1
    user.navigation_mode = "unified"
    user.game_action_button = "space" 
    user.highlight_proximity_x = 100
    user.highlight_proximity_y = 100
    user.grid_column_threshold = 500
    user.grid_row_threshold = 40
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
^walk$: user.set_global_variable("repeat_button_speed", 800)
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
^go <user.word>$: user.navigate_to_word_wasd_with_action(word, "chained_battle_border.png")

^quack: user.press_key_x_times("escape", 4, 2)

^{user.wasd_arrows} <number>$: 
    user.press_key_x_times(user.wasd_arrows, number, 0.5)

# Debug commands for grid navigation
^test grid$: user.test_grid_analysis()
^test nav <user.word>$: user.test_grid_navigation(word)
^debug grid <user.word>$: user.navigate_step_grid(word, "chained_battle_border.png", true, 1, null)
^find text <user.word>$: user.get_text_coordinates(word)
^debug step <user.word>$: user.navigate_step(word, "chained_battle_border.png", true, 5, false, "")
^find cursor$: user.find_template_flexible("chained_battle_border.png")
^test flexible cursor$: user.find_template_flexible("chained_battle_border.png")