mode: user.game
app: NVidia GeForce NOW
title: /disco elysium/i
-
settings():
    key_wait = 20
tag(): user.user_arrows
tag(): user.cardinal_directions

[left] (touch | click) <user.timestamped_prose>$:
    user.click_text(timestamped_prose)

^<number_small>$: key("{number_small}")

^stop$: user.game_stop()

back: key("escape")
face(raise_eyebrows): key("tab:down")
face(raise_eyebrows:stop): key("tab:up")

#(bang | fun | thank | fine | base | bran | burn | spang | bank | banks | bin | burn | hang)$: key("return") 
face(pucker_lips_right): key("return")
^(back | brack | buck | pack | track)$: key("escape")

^character$: key("c")
^inventory$: key("i")
^thinking$: key("t")
^(journal | channel)$: key("j")
^help$: key("f1")
^map$: key("m")
quick save: key("f5")