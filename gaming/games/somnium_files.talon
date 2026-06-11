user.active_manual_game: ai the somnium files
mode: user.game
app: moonlight
-

parrot(click): key("enter")
parrot(tch): key("esc")

^dialogue$: user.set_single_press_button("c")

^menu$: key("tab")
^whale$: key("w")
^air$: key("a")
^sun$: key("s")
^drum$: key("d")
^look$: key("space")

^<user.arrow_keys>$:
    key("{arrow_keys}:down")
    sleep(1)
    key("{arrow_keys}:up")
