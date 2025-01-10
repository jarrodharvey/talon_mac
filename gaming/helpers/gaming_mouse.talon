user.eye_tracker_active: yes
mode: user.game
-
face(smile):
    user.conditional_click()
face(smile:stop):
    user.mouse_button_up(0)

parrot(raspberry):
    user.super_click(0.01)
    user.super_click(0.01)
    user.super_click(0.01)

face(jaw_open:start): 
    user.set_global_variable("mouth_open", "yes")
    user.eye_tracker_off()
face(jaw_open:stop): 
    user.set_global_variable("mouth_open", "no")
    user.eye_tracker_on()

parrot(kiss):
    mouse_click(1)

^drag mouse$: user.set_global_variable("mouse_dragging", "yes")
^stop drag$: user.set_global_variable("mouse_dragging", "no")

^calibrate eye tracker$: tracking.calibrate()