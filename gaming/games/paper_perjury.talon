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
^rapid$: user.set_repeat_button("space", 1)

^skip$: key("ctrl:down")

^stop$: user.game_stop()

^up$: 
    user.mouse_scroll_down()
    repeat(20)

^down$: 
    user.mouse_scroll_up()
    repeat(20)

^scroll bottom$: 
    user.mouse_scroll_up()
    repeat(100)

^right$: user.game_click_spot("paper right")
^left$: user.game_click_spot("paper left")