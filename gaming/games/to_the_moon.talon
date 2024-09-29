app: Just a To the Moon Series Beach Episode
mode: user.game
-

settings():
    key_wait = 30

tag(): user.user_arrows
tag(): user.cardinal_directions    

^click <user.timestamped_prose>$:
    user.click_text(timestamped_prose)
    user.super_click()

^stop$: user.game_stop()

^mash$: user.set_repeat_button("return", 5)

parrot(click): 
    user.game_stop()
    key("space:up")
    key("return")
parrot(tch): 
    user.game_stop()
    key("escape")

^scan start$:  key("space:down")
^scan stop$:  key("space:up")