mode: user.game
app: NVidia GeForce NOW
title: /baldur's gate 3/i
user.boxes_gaming_status: off
-
tag(): user.cardinal_directions

[left] (touch | click) <user.timestamped_prose>$:
    user.click_text(timestamped_prose)
    user.super_click()

^calibrate eye tracker$: tracking.calibrate()

#^boxes$: user.boxes_gaming_status_on()

^scroll$: 
    user.mouse_scroll_down()
    repeat(300)

^scroll up$: 
    user.mouse_scroll_up()
    repeat(300)

^camera$: 
    key("`")
    user.mouse_scroll_down()
    repeat(100)

^menu$: key("escape")

^zoom out$: 
    user.mouse_scroll_down()
    repeat(100)
^zoom in$: 
    user.mouse_scroll_up()
    repeat(5)

^tactical$: key("o")

parrot(click): 
    key("backspace:up")
    key("backspace:down")
^dark$: key("backspace:up")

^<number_small>$: key("{number_small}")

^quick save$: key("f5")

^inventory$: key("i")
^map$: key("m")

^loot$: key("space") 
^next$: key("space") 

parrot(tch): key("escape")

^inspect$: key("t")

face(brow_outer_up_left:start): key("e:down")
face(brow_outer_up_left:stop): key("e:up")

face(brow_down_right:start): key("q:down")
face(brow_down_right:stop): key("q:up")

^journal$: key("j")

^recipes$: key("h")

^jump$: key("z")

^throw$: key("x") 

^highlight$: key(";")

^hide$: key("c")

^face tester$: user.face_tester_toggle()

^search <user.word>$: 
    insert("{user.word}") 
    key("return")

^spellbook$: key("k")