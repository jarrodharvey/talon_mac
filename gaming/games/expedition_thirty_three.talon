user.active_manual_game: expedition 33
mode: user.game
not mode: user.gaze_ocr_disambiguation
app: moonlight
-

settings():
    key_hold = 100 
    user.mouse_movement_speed = 900
    user.mouse_movement_distance = 300

tag(): user.wasd_directions_3d
tag(): user.8bitdo_3d_movement

^tap <number>$:
    user.click_then_wait(0.5)
    repeat(number - 1)

^zoom in$: 
    user.mouse_scroll_down()
    repeat(1000)
^zoom out$: 
    user.mouse_scroll_up()
    repeat(1000)

^camp$: key("g")

^<user.letters>$: key(letters)
# Unrecognized letters
^whale$: key("w")

^map$: key("m")

flex grid: user.flex_grid_place_window()
[flex] grid close: user.flex_grid_deactivate()

# Common parrot commands
parrot(click): 
    user.game_stop()
    key(e)
    key(f)
parrot(tch): key(esc)
parrot(raspberry): key("space")

^stop$: user.game_stop()

^(walk | run)$: 
    user.game_stop()
    key(0)
    sleep(500ms)
    user.set_global_variable("looking_around", "no")
    key("w:down")

^character$: key("t")

^(mash | dialogue)$: 
    key("f")
    user.set_repeat_button("f", 6)
^battle$: 
    user.set_repeat_button("f", 1)
^discard$: 
    key("space")
    user.set_repeat_button("space", 5)

^menu$: key("tab")

^healing$: 
    key("q:down") 
    sleep(2s)   
    key("q:up")

^(upgrade | unlock)$: 
    key("f:down")
    sleep(1500ms)
    key("f:up")

^look$: 
    user.game_stop()
    user.set_global_variable("looking_around", "yes")
^move$: 
    user.set_global_variable("looking_around", "no")
    key("w:down")

^look right$: user.move_mouse_relative("right", 500)

# Battle commands
^items$: key("w")
^skills$: key("e")
^attack$: key("f")
^smash$: 
    key("f")
    sleep(500ms)    
    key("f")
^(assault | immolation)$: 
    key("q")
    sleep(500ms)
    key("f")
^(charge | lance)$: 
    key("w")
    sleep(500ms)
    key("f")
^aim$: mouse_click(1)
^flee$: 
    key("c:down") 
    sleep(1200ms)
    key("c:up")
# Dodge
parrot(kiss): key("q")
# Parry is parrot(click)
# Fire button
key(keypad_9): mouse_click(0)

