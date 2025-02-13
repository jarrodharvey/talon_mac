mode: user.game
#app: NVidia GeForce NOW
#title: /baldur's gate 3/i
app: moonlight
user.active_manual_game: bg3
-
tag(): user.cardinal_directions

^face tester$: user.face_tester_toggle()

^scroll$: 
    user.mouse_scroll_up()
    repeat(300)

^scroll up$: 
    user.mouse_scroll_down()
    repeat(300)

^camera$: 
    key("`")
    user.mouse_scroll_up()
    repeat(100)

^zoom in$: 
    user.mouse_scroll_down()
    repeat(100)
^zoom out$: 
    user.mouse_scroll_up()
    repeat(5)

^tactical$: key("o")

parrot(click): 
    key("backspace:up")
    key("backspace:down")
^dark$: key("backspace:up")

^<number_small>$: key("{number_small}")
^first$: key("1")
^second$: key("2")
^fourth$: key("4")

^quick save$: key("f5")

^inventory$: key("i")
^map$: 
    key("backspace:up")
    user.game_stop()
    key("m")

^extract$: key("space") 
^turn$: key("space") 

parrot(tch): key("escape")

^inspect$: key("t")

face(brow_outer_up_left:start): user.press_key_if_condition_met("e:down", "mouth_open", "no")
face(brow_outer_up_left:stop): key("e:up")

face(brow_down_right:start): user.press_key_if_condition_met("q:down", "mouth_open", "no")
face(brow_down_right:stop): key("q:up")

^journal$: key("j")

^recipes$: key("h")

^jump$: key("z")

^throw$: key("x") 

^highlight$: key(";")

^hide$: key("c")

^search <user.word>$: 
    key("backspace:up")
    user.game_stop()
    user.click_image("bg3_search1.png")
    user.click_image("bg3_search2.png")
    insert("{user.word}") 
    key("return")

^page$: 
    user.click_image("bg3_next_page.png")

^latest$: 
    user.click_image("bg3_filter.png")
    sleep(1s)
    user.click_image("bg3_latest.png")

^spellbook$: key("k")

^{user.direction} [<number_small>]$:
    user.move_map(direction, number_small or 1)

^inspiration$: key("p")

^powers$: key("b")

^mash$: user.set_repeat_button("space", 0.5)

^stop$: user.game_stop()

^take turns$: key("shift-space")

# Character buttons
^num one$: key("f1")
^num two$: key("f2")
^num three$: key("f3")
^num four$: key("f4")

^double <number_small>$: 
    user.double_click_then_wait(0.5)
    repeat(number_small - 1)