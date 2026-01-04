mode: user.game
app: moonlight
user.active_manual_game: crusader kings
-
settings():
    key_hold = 90
    user.super_click_duration = 0.8
    user.uses_wasd = true
    user.keep_tracker_on_ocr = true

tag(): user.panning

parrot(click): 
    user.game_stop()
    key("return")

parrot(tch): 
    user.game_stop()
    key("escape")

# Lock tooltip then click new text 
^lock <user.timestamped_prose>$:
    mouse_click(2)
    sleep(500ms)
    user.move_cursor_to_word(timestamped_prose)
    sleep(500ms)
    mouse_click(0)

# Zoom in/out
^out [{user.number_small}]$: 
    repeat_times = user.simple_math("{number_small or 1} * 100")
    user.mouse_scroll_up()
    repeat(repeat_times)

^in [{user.number_small}]$: 
    repeat_times = user.simple_math("{number_small or 1} * 100")
    user.mouse_scroll_down()
    repeat(repeat_times)

^down$: 
    user.mouse_scroll_up()
    repeat(300)

^up$:
    user.mouse_scroll_down()
    repeat(300)

^home$: key("home")
^pause$: key("space")

^stop$: user.game_stop()

^fast$: user.set_global_variable("repeat_button_speed", 250)
^normal$: user.set_global_variable("repeat_button_speed", 500)
^slow$: user.set_global_variable("repeat_button_speed", 1000)

^character$: user.game_click_spot("crusade character")

^tutorial$: user.set_repeat_button("return", 1)

^off$: user.game_click_spot("crusade off") 

# shortcuts
^realm$: key("f2")
^council$: key("f4")
^court$: key("f5")
^intrigue$: key("f6")