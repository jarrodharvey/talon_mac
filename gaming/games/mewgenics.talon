mode: user.game
app: Moonlight
user.active_manual_game: mewgenics
-

settings():
    user.ocr_click_delay = 200
    user.super_click_duration = 0.8
    key_hold = 10

parrot(tch): key("esc")
parrot(click): mouse_click(1)

^dialogue$: user.set_repeat_button("click", 5)

^go$: user.double_click_then_wait()

^move$: key("1")
^weapon$: key("2")
^trinket$: key("3")

^attack$: key("q")

^one$: key("w")
^two$: key("e")
^three$: key("r")
^four$: key("t")
^five$: key("y")

^turn$: key("`")

^inventory$: user.game_click_spot("cut inventory")
^day$: user.game_click_spot("cat they")

