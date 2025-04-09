user.active_manual_game: pywright
mode: user.game
app: moonlight
user.boxes_gaming_status: off
-
settings():
    user.super_click_duration = 0.05

parrot(click): key("return")
parrot(tch): key("tch")

^save game$: key("f5")
^load game$: key("f7")

^mash$: user.set_repeat_button("return", 5)

^back$: user.click_spot("attorney back")

^next$: user.click_spot("attorney next")
^previous$: user.click_spot("attorney previous")