user.active_manual_game: expedition 33
mode: user.game
app: moonlight
-

settings():
    key_hold = 70
    user.mouse_movement_speed = 400
    user.mouse_movement_distance = 300

tag(): user.wasd_directions_3d
tag(): user.8bitdo_3d_movement

^<user.letters>$: key(letters)

# Common parrot commands
parrot(click): 
    user.game_stop()
    key(e)
    key(f)
parrot(tch): key(esc)
parrot(raspberry): key("space")

^stop$: user.game_stop()

^walk$: 
    user.game_stop()
    key(0)
    sleep(500ms)
    key("w:down")

^(mash | dialogue)$: 
    key("f")
    user.set_repeat_button("f", 5)
^discard$: 
    key("space")
    user.set_repeat_button("space", 5)

# Battle commands
^items$: key("w")
^skills$: key("e")
^attack$: key("f")
^assault$: key("q")
^overcharge$: key("w")