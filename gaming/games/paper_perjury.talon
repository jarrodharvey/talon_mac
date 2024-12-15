user.active_manual_game: paper perjury
mode: user.game
app: steamstreamingclient
app: moonlight
-

parrot(click): key("return")
parrot(tch): 
    user.game_stop()
    key("escape")

^mash$: user.set_repeat_button("space", 4)

^skip$: key("ctrl:down")

^stop$: user.game_stop()