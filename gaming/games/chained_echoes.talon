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
    user.navigation_interval = 500
    # Cube settings for character portrait navigation
    user.cube_min_width = 40
    user.cube_min_height = 25
    user.cube_max_count = 30
    # Bright blue cubes to differentiate from flex-mouse-grid purple
    user.cube_background_color = "00BFFF"
    user.cube_stroke_color = "0080FF"
# Enable arrow key movement commands
tag(): user.8bitdo_wasd_diagonal
tag(): user.wasd_directions
tag(): user.pathfinding_cubes

# Parrot sounds for common actions - click sound triggers main action button
parrot(click): 
    user.game_stop()
    key("space")
# Tch sound for cancel/back actions
parrot(tch): 
    user.game_stop()
    key("escape")

# Movement speed controls for exploration
^walk$: user.set_global_variable("repeat_button_speed", 800)
^jog$: user.set_global_variable("repeat_button_speed", 500)
^sprint$: user.set_global_variable("repeat_button_speed", 250)
^tiptoe$: user.set_global_variable("repeat_button_speed", 1000)

^menu$: 
    user.game_stop()
    key("i")

# Automated dialogue advancement with different speeds
^tutorial$: user.set_repeat_button("space", 5)
^dialogue$: user.set_repeat_button("space", 4)

^stop$: user.game_stop()

# Rapid button mashing for dialogue skip
^mash$: user.set_repeat_button("space", 0.5)
^careful$: user.set_repeat_button("space", 2)

^map$: 
    user.game_stop()
    key("m")

double: user.press_key_x_times("space", 2, 1)
^triple$: user.press_key_x_times("space", 3, 1)

# Dynamic menu navigation - navigate to any word using OCR
^go <user.word>$: user.navigate_to_word(word)
^save game$: 
    user.game_stop()
    key("i")
    sleep(1.5)
    user.press_key_x_times("w", 1, 0.5)
    user.press_key_x_times("space", 4, 0.5)
    user.press_key_x_times("esc", 3, 0.5)

^set skills$: 
    user.game_stop()
    key("i")
    sleep(1.5)
    user.press_key_x_times("s", 2, 0.5)
    key("space")

^equipment$: 
    user.game_stop()
    key("i")
    sleep(1.5)
    user.press_key_x_times("s", 1, 0.5)
    key("space")

^optimization$: 
    user.game_stop()
    key("i")
    sleep(1.5)
    user.press_key_x_times("s", 1, 0.5)
    key("space")
    sleep(0.5)
    key("i")
    sleep(0.5)
    key("d")
    sleep(0.5)
    key("space")
    user.press_key_x_times("esc", 3, 0.5)

^journal$: 
    user.game_stop()
    key("i")
    sleep(1.5)
    user.press_key_x_times("s", 5, 0.5)
    key("space")

^ultra$: key("r")
^optimize$: key("i")
^knock$: key("e")
^previous$: key("q")
^level up$: key("i")
^teleport$: key("i")
^(location | quest) info$: key("e")
^select all$: key("m") 
^switch$: 
    key("e")
    sleep(1s)
    key("e")

key(=):
    user.set_repeat_button("space", 4)
    key("space")
    sleep(0.5)
    user.conditional_image_button_press("space", "chained_chat.png", 4000, true)

^quack: user.press_key_x_times("escape", 4, 2)

{user.wasd_arrows} [<number>]: 
    user.press_key_x_times(user.wasd_arrows, number or 1, 0.5)

bang: key("space")

^restart game$: 
    user.game_stop()
    key("alt-escape")
    sleep(1.5)
    user.click_image("steam_stop.png")
    sleep(1.5)
    user.click_image("steam_confirm.png")
    sleep(6)
    user.click_image("steam_play.png")

### Debugging
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

