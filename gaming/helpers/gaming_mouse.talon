user.eye_tracker_active: yes
mode: user.game
-
#settings():
#    user.wink_button_left = "rmb"  

face(smile): user.super_click()

face(jaw_open):
    user.super_click(0.01)
    user.super_click(0.01)
    user.super_click(0.01)

face(mouth_shrug_lower):
    mouse_click(1)