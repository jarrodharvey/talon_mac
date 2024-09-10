mode: user.game 
user.boxes_gaming_status: on
-

# Uncomment the below lines and put them into your Talon file for your game that uses boxes.
#^boxes$: user.boxes_gaming_status_on()
# Put this bit into the header.
# user.boxes_gaming_status: off

^<number>$: 
    user.flex_grid_go_to_box(number or 1, 0)
    sleep(2s)
    user.flex_grid_setup_boxes()
^double <number>$:
    user.flex_grid_go_to_box(number or 1, 0)
    sleep(30ms)
    mouse_click(0)
^visit <number>$: 
    user.flex_grid_go_to_box(number or 1, -1)
^(clean | claim | quay | play | quaint | queen)$: user.boxes_gaming_status_off()