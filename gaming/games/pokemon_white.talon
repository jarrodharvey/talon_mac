user.active_manual_game: pokemon white
mode: user.game
app: moonlight
-

settings():
    key_hold = 30

tag(): user.cardinal_directions
tag(): user.user_arrows

parrot(click): key("x")
bang$: key("x")
parrot(tch): key("z")

^start$: key("enter")
^menu$: key("s")

^dialogue$: user.set_repeat_button("z", 3)
^speed$: user.set_repeat_button("x", 0.5)
