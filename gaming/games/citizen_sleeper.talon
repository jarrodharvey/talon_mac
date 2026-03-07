mode: user.game
app: Moonlight
user.active_manual_game: citizen sleeper
-

settings():
    user.super_click_duration = 0.8
    key_hold = 10
    user.disable_hud_log_exclusion = 1

parrot(click): user.super_click()
parrot(tch): user.click_image("citizen_leave.png")

^bang$: user.click_image("citizen_continue.png")

^dialogue$: user.set_repeat_button("cit2_continue.png", 10, "image")

^down [{user.number_small}]$:
    hold_ms = user.simple_math("{number_small or 1} * 100")
    user.hold_key("s", hold_ms)

^up [{user.number_small}]$:
    hold_ms = user.simple_math("{number_small or 1} * 100")
    user.hold_key("w", hold_ms)

^left [{user.number_small}]$:
    hold_ms = user.simple_math("{number_small or 1} * 100")
    user.hold_key("a", hold_ms)

^right [{user.number_small}]$:
    hold_ms = user.simple_math("{number_small or 1} * 100")
    user.hold_key("d", hold_ms)

^down twice$: user.hold_key("s", 400)
^up twice$: user.hold_key("w", 400)

^bring <user.prose>$: user.drag_to_text(prose)

^(survive | quests)$: user.game_click_spot("citizens survive")
^operator$: user.game_click_spot("citizen operator")
^end cycle$: user.click_image("ci_end_cycle.png")
^action$: user.click_image("citizen_action.png")
^data$: user.click_image("citizen_data.png")

^cross$: 
    user.click_image("citizen_transit.png")
    user.click_image("citizen_cross.png")

^ascend$: 
    user.click_image("citizen_elevator_up2.png")
    user.click_image("citizen_ascend.png")

^descend$:
    user.click_image("citizen_elevator.png")
    user.click_image("citizen_descend.png")

^rig$: user.click_image("sleeper_rig.png")
^map$: user.game_click_spot("sleeper map")
^explore$: user.game_click_spot("sleeper explore")

^restart game$: 
    user.game_stop()
    key("alt-escape")
    sleep(1.5)
    user.click_image("steam_stop.png")
    sleep(1.5)
    user.click_image("steam_confirm.png")
    sleep(6)
    user.click_image("steam_play.png")

^confirm$: user.click_image("sleep_confirm.png")
^menu$: key("escape")