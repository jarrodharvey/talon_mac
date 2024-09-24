user.eye_tracker_active: yes
mode: user.game
-
settings():
    user.wink_button_left = "rmb"  

face(smile): mouse_click()

face(jaw_open):
    mouse_click()
    mouse_click()

#face(frown): mouse_click(1) 