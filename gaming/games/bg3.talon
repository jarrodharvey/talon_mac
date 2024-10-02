mode: user.game
app: NVidia GeForce NOW
title: /baldur's gate 3/i
user.boxes_gaming_status: off
-
settings():
    key_wait = 70
tag(): user.user_arrows

[left] (touch | click) <user.timestamped_prose>$:
    user.click_text(timestamped_prose)
    user.super_click()

^calibrate eye tracker$: tracking.calibrate()

^boxes$: user.boxes_gaming_status_on()

^scroll$: 
    user.mouse_scroll_down()
    repeat(300)

^scroll up$: 
    user.mouse_scroll_up()
    repeat(300)
