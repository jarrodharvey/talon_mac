user.active_manual_game: ai the somnium files
mode: user.game
app: moonlight
-

settings():
    user.gamepad_east_single_key = "c"

parrot(click): key("enter")
parrot(tch): key("esc")

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
