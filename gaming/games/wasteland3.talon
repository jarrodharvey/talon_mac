user.active_manual_game: wasteland 3
mode: user.game
app: moonlight
-

settings():
    user.game_action_button = "enter"
    user.default_action_button_interval = 1

tag(): user.user_arrows
tag(): user.cardinal_directions

parrot(click):
    user.game_stop()
    key("enter")

parrot(tch):
    user.game_stop()
    key("escape")

^scroll [{user.number_small}]$:
    repeat_times = user.simple_math("{number_small or 1} * 80")
    user.mouse_scroll_up()
    repeat(repeat_times)

^scroll up [{user.number_small}]$:
    repeat_times = user.simple_math("{number_small or 1} * 80")
    user.mouse_scroll_down()
    repeat(repeat_times)

^touch$: user.super_click()

^stop$: user.game_stop()

# Camera (INSERT→keypad_0, DELETE→fn-delete, HOME→fn-home on Mac via Moonlight)
^snap$: key("fn-home")
^zoom$:
    key("keypad_0:down")
    sleep(500ms)
    key("keypad_0:up")
^zoom out$:
    key("fn-delete:down")
    sleep(500ms)
    key("fn-delete:up")
^rotate [right]$: key("q")
^rotate left$: key("e")
^reset camera$: key("backspace")

# End turn / group mode
^turn$: key("space")

# Character selection
^next$: key("tab")
^previous$: key("`")
^character one$: key("keypad_1")
^character two$: key("keypad_2")
^character three$: key("keypad_3")
^character four$: key("keypad_4")
^character five$: key("keypad_5")
^character six$: key("keypad_6")

# Character screens
^attributes$: key("c")
^inventory$: key("j")
^skills$: key("k")
^perks$: key("p")
^reputation$: key("l")
^map$: key("m")

# Combat actions
^attack$: key("ctrl")
^switch [weapon]$: key("x")
^reload$: key("r")
^precision [strike]$: key("f")
^ambush$: key("v")
^defend$: key("b")
^prepare$: key("n")
^crouch$: key("z")

# Misc
^grid$: key("g")
^radio$: key("/")
^horn$: key("h")
^highlight$: key("shift")

# Save / load
^quick save$: key("f5")
^quick load$: key("f9")

# Dialogue advancement
^dialogue$: user.set_repeat_button("enter", 5)
^mash$: user.set_repeat_button("enter", 0.5)

# OCR menu navigation (requires cursor templates in gaming/cursors/wasteland3/)
^go <user.prose>$: user.navigate_to_word(prose)

# Debug
^debug text$: user.debug_all_text_coordinates()
^debug cursor$: user.debug_cursor_position()
^debug path$: user.debug_pathfinding_state()
