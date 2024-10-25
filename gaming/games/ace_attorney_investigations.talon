user.active_manual_game: ace attorney investigations
mode: user.game
app: steamstreamingclient
-

parrot(click): key("space")
parrot(tch): key("z")

^mash$: user.set_repeat_button("space", 5)

^touch <user.timestamped_prose>$:
    user.click_text(timestamped_prose)
    user.super_click()

^run$: key("shift")
^organizer$: key("e")
^logic$: key("q")
^press$: key("q")
^partner$: key("t")
^present$: key("t")
^options$: key("g")
^history$: key("r")