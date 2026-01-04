mode: user.game
app: moonlight
user.active_manual_game: crusader kings
-

# settings():
#     key_hold = 90
#     user.super_click_duration = 0.8
#     user.uses_wasd = true

# tag(): user.8bitdo_wasd_diagonal

# Zoom in/out
^out [{user.number_small}]$: 
    repeat_times = user.simple_math("{number_small} * 100")
    user.mouse_scroll_up()
    repeat(repeat_times)

^in [{user.number_small}]$: 
    repeat_times = user.simple_math("{number_small} * 100")
    user.mouse_scroll_down()
    repeat(repeat_times)

^home$: key("home")

^stop$: user.game_stop()