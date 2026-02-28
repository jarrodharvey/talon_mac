mode: user.game
app: Moonlight
user.active_manual_game: citizen sleeper
-

settings():
    user.super_click_duration = 0.8
    key_hold = 10

parrot(click): user.super_click()

^bang$: user.click_image("citizen_continue.png")

^dialogue$: user.set_repeat_button("citizen_continue.png", 10, "image")

^down [{user.number_small}]$: 
    repeat_times = user.simple_math("{number_small or 1} * 25")
    user.mouse_scroll_up()
    repeat(repeat_times)

^up [{user.number_small}]$: 
    repeat_times = user.simple_math("{number_small or 1} * 25")
    user.mouse_scroll_down()
    repeat(repeat_times)


^left [{user.number_small}]$: 
    repeat_times = user.simple_math("{number_small or 1} * 25")
    key("a")
    repeat(repeat_times)

^right [{user.number_small}]$:
    repeat_times = user.simple_math("{number_small or 1} * 25")
    key("d")
    repeat(repeat_times)

^bring <user.prose>$: user.drag_to_text(prose)

^survive$: user.game_click_spot("citizens survive")
^operator$: user.game_click_spot("citizen operator")
^end cycle$: user.click_image("end_cycle.png")
^action$: user.click_image("citizen_action.png")
