mode: user.game
app: Moonlight
user.active_manual_game: citizen sleeper
-

settings():
    user.super_click_duration = 0.8
    key_hold = 10

parrot(click): user.super_click()

^bang$: user.click_image("citizen_continue.png")

^dialogue$: user.set_repeat_button("citizen_continue.png", 7, "image")

