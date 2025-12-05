user.active_manual_game: octopath traveler
mode: user.game
app: moonlight
-

settings():
    key_wait = 20
    user.super_click_duration = 0.8
    user.travel_distance = 1
    user.navigation_mode = "unified"
    user.game_action_button = "space" 
    user.highlight_proximity_x = 60
    user.highlight_proximity_y = 20
    user.cursor_directory = "octopath_traveler"
    user.grid_column_threshold = 500
    user.grid_row_threshold = 40
    user.uses_pathfinding = true
    user.uses_wasd = true
    user.navigation_interval = 500
    user.default_action_button_interval = 1
# Enable arrow key movement commands
tag(): user.8bitdo_wasd_diagonal
tag(): user.wasd_directions

# Parrot sounds for common actions - click sound triggers main action button
parrot(click): 
    user.game_stop()
    key("return")

# Automated dialogue advancement with different speeds
^dialogue$: user.set_repeat_button("return", 8)
^exposition$: user.set_repeat_button("return", 7)

^stop$: user.game_stop()

# Rapid button mashing for dialogue skip
^mash$: user.set_repeat_button("return", 0.5)
^battle$: user.set_repeat_button("return", 2)

^close$: key("c")
^map$: key("t")
^menu$: key("i")
^confirm$: key("f")
^toggle pages$: key("f")
^(counsel | cancel)$: key("c")

^save game$:
    user.betterinput_simple("return |500ms space")
