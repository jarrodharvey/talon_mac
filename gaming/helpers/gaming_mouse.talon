user.eye_tracker_active: yes
-
face(smile): user.super_click()

face(mouth_left):
    user.super_click(0.01)
    user.super_click(0.01)
    user.super_click(0.01)

face(jaw_open:start): user.eye_tracker_off()
face(jaw_open:stop): user.eye_tracker_on()

face(mouth_right):
    mouse_click(1)