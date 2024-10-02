user.eye_tracker_active: yes
mode: user.game
-
face(smile:start): user.mouse_button_down(0)
face(smile:stop): user.mouse_button_up(0)

face(jaw_open):
    user.super_click(0.01)
    user.super_click(0.01)
    user.super_click(0.01)

face(mouth_shrug_lower):
    mouse_click(1)