mode: user.game
tag: user.8bitdo_3d_movement
-

# Bindings for the 8bitdo selite controller, passed through hid-remapper.
# Used primarily for directional pad control

key(keypad_4): 
    user.game_stop()
    key("a:down")
key(keypad_6):
    user.game_stop()
    key("d:down")
key(keypad_8):  
    user.game_stop()
    key("w:down")
key(keypad_2):
    user.game_stop()
    key("s:down")

# Forward diagonal movement
key(;): 
    user.game_stop()
    key("w:down")
    key("a:down")
key([): 
    user.game_stop()
    key("w:down")
    key("d:down")

key(pageup:down): user.stop_and_press_key("w")
key(pagedown:down): user.stop_and_press_key("s")
key(home:down): user.stop_and_press_key("a")
key(end:down): user.stop_and_press_key("d")