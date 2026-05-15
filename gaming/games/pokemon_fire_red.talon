user.active_manual_game: pokemon fire red
mode: user.game
app: mGBA
-

settings():
    key_hold = 70
    user.navigation_mode = "unified"
    user.cursor_directory = "fire_red"
    user.game_action_button = "x" 
    user.highlight_proximity_x = 90
    user.highlight_proximity_y = 40
    user.uses_pathfinding = true
    user.navigation_interval = 100
    user.uses_wasd = false
    user.disable_hud_log_exclusion = 0

tag(): user.8bitdo_selite
tag(): user.user_arrows
tag(): user.cardinal_directions

# mGBA button mappings:
# A: x
# B: z
# Start: enter
# Select: shift
# D-pad: arrow keys

parrot(click): 
    user.game_stop()
    key("x")
parrot(tch): key("z")

^dialogue$: user.set_repeat_button("z", 3)
^battle$: user.set_repeat_button("x", 0.5)

key(`): 
    user.set_repeat_button("z", 2)
    user.conditional_image_button_press("x", "unbound_triangle.png", 2000, true, 0, true, "x", "x")

^walk$: user.set_global_variable("repeat_button_speed", 500)
^jog$: user.set_global_variable("repeat_button_speed", 300)
^sprint$: user.set_global_variable("repeat_button_speed", 100)
^tiptoe$: user.set_global_variable("repeat_button_speed", 800)

bang: key("x")
dub|double: 
    user.game_stop()
    user.betterinput_with_sleep("x:2", "1000ms")
trip: 
    user.game_stop()
    user.betterinput_with_sleep("x:3", "1000ms")

^back$: key("z")
^dack$: user.betterinput_with_sleep("z:2", "1500ms")
^track$: user.betterinput_with_sleep("z:3", "1500ms")
^quack$: user.betterinput_with_sleep("z:4", "1500ms")

^dang$: 
    user.game_stop()
    user.betterinput_with_sleep("down | x", "500ms")

^rang$: 
    user.game_stop()
    user.betterinput_with_sleep("right | x", "500ms")

^rubble$: 
    user.game_stop()
    user.betterinput_with_sleep("right | x | x", "500ms")

^lang$: 
    user.game_stop()
    user.betterinput_with_sleep("left | x", "500ms")

^menu$: 
    user.game_stop()
    key("enter")

# Visual debug markers for pathfinding
^path debug [<user.prose>]$:
    target = prose or "Fight"
    user.show_pathfinding_debug_markers(target)

^path dismiss$:
    user.hide_pathfinding_debug_markers()

^actions <number>$: user.set_pathfinding_global_variable("default_action_button_count", number)

^cycle$: key("backspace")

^(detail | description | catch)$: key("a")

^capture$: user.set_repeat_button("a", 1)

^next$: 
    key("x")
    user.conditional_image_button_press("z", "file_red_yes_no.png", 1000, false)

^door$: 
    user.game_stop()
    key("x")
    key("up:down")

^pokemon$: 
    user.game_stop()
    key("s")

^item$: 
    user.game_stop()
    key("x")
    sleep(4s)
    key("x")