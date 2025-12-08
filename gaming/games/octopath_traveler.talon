user.active_manual_game: octopath traveler
mode: user.game
app: moonlight
-

settings():
    key_hold = 16
    user.super_click_duration = 0.8
    user.travel_distance = 1
    user.navigation_mode = "vertical"
    user.game_action_button = "return" 
    user.highlight_proximity_x = 80
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
parrot(tch): 
    user.game_stop()
    key("c")

# Automated dialogue advancement with different speeds
^dialogue$: user.set_repeat_button("return", 6)
^chat$: user.set_repeat_button("return", 2)
^exposition$: user.set_repeat_button("return", 10)
^battle$: user.set_repeat_button("return", 0.5)

^stop$: user.game_stop()

^close$: key("c")
^map$: key("t")
^menu$: 
    user.game_stop()
    key("i")
^confirm$: key("f")
^open$: 
    user.game_stop()
    user.betterinput_with_sleep("f | return", "2000ms")
^examine$: key("f")
^toggle pages$: key("f")
^(counsel | cancel)$: key("c")
^inquire$: 
    user.conditional_image_button_press("return", "path_chat.png", 2500, true, 0, true, "space |3000ms return |3000ms return")
^tooltips$: key("space")

^save game$:
    user.game_stop()
    user.betterinput_with_sleep("return:3 | c:2", "1000ms")

^dub$: user.betterinput_with_sleep("return:2", "2000ms")
double$: 
    key("return")
    sleep(2000ms)
    key("return")
^dack$: user.betterinput_with_sleep("c:2", "2000ms")

# Visual debug markers for pathfinding
^path debug [<user.prose>]$:
    target = prose or "Attack"
    user.show_pathfinding_debug_markers(target)

^path dismiss$:
    user.hide_pathfinding_debug_markers()

key(`):
    user.conditional_image_button_press("return", "path_chat.png", 2500, true, 0, true, "return")

^walk$: user.set_global_variable("repeat_button_speed", 750)
^jog$: user.set_global_variable("repeat_button_speed", 500)
^sprint$: user.set_global_variable("repeat_button_speed", 250)
^tiptoe$: user.set_global_variable("repeat_button_speed", 1000)

^actions <number>$: user.set_pathfinding_global_variable("default_action_button_count", number)

bang: key("return")

{user.wasd_arrows} [<number>]: 
    user.press_key_x_times(user.wasd_arrows, number or 1, 0.5)

{user.wasd_arrows} twice: 
    user.press_key_x_times(user.wasd_arrows, 2, 0.5)

^unboost$: key("q")

^dang$: user.betterinput_simple("s |1000ms return")

^boost [<number>]$: 
    user.press_key_x_times("e", number or 1, 0.5)