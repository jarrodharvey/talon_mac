user.active_manual_game: chained echoes
mode: user.game
app: moonlight
-

settings():
    user.super_click_duration = 0.8
    user.travel_distance = 1
    user.navigation_mode = "unified"
    user.game_action_button = "space" 
    user.highlight_proximity_x = 70
    user.highlight_proximity_y = 15
    user.cursor_directory = "chained_echoes"
    user.grid_column_threshold = 500
    user.grid_row_threshold = 40
    user.uses_pathfinding = true
    user.uses_wasd = true
    user.navigation_interval = 800
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

^menu$: key("i")

^quick save$: key("f5")
^quick load$: key("f9")

# Automated dialogue advancement with different speeds
^tutorial$: user.set_repeat_button("space", 5)
^dialogue$: user.set_repeat_button("space", 2.5)

^stop$: user.game_stop()

# Rapid button mashing for dialogue skip
^mash$: user.set_repeat_button("space", 0.5)
^careful$: user.set_repeat_button("space", 2)

^map$: key("m")

^double$: user.press_key_x_times("space", 2, 1)

# Dynamic menu navigation - navigate to any word using OCR
^go <user.word>$: user.navigate_to_word_with_action(word)

# Debug functions
^debug text$: user.debug_all_text_coordinates()
^debug cursor$: user.debug_cursor_position()
^debug path$: user.debug_pathfinding_state()

# Visual debug markers for pathfinding
^path debug [<user.word>]$:
    target = word or "Attack"
    user.show_pathfinding_debug_markers(target)

^path dismiss$:
    user.hide_pathfinding_debug_markers()

^quack: user.press_key_x_times("escape", 4, 2)

^{user.wasd_arrows} <number>$: 
    user.press_key_x_times(user.wasd_arrows, number, 0.5)
