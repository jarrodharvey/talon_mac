user.eye_tracker_active: yes
mode: user.game
-
#face(smile): user.super_click()

face(smile:start):
    user.mouse_button_down(0)
face(smile:stop):
    user.mouse_button_up(0)

face(mouth_shrug_upper):
    user.super_click(0.01)
    user.super_click(0.01)
    user.super_click(0.01)

face(jaw_open:start): 
    user.set_global_variable("mouth_open", "yes")
    user.eye_tracker_off()
face(jaw_open:stop): 
    user.set_global_variable("mouth_open", "no")
    user.eye_tracker_on()

face(mouth_right):
    mouse_click(1)

# Clicking in games is weird so I've set this up to allow for a drag and click mode.
^gaming drag$: user.set_global_variable("mouse_dragging", "yes") 
^gaming click$: user.set_global_variable("mouse_dragging", "no") 

^calibrate eye tracker$: tracking.calibrate()