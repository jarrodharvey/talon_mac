user.hiss_dpad_active: yes
mode: user.game
-

face(blink_left:start): user.start_left_eye_closed_cron("left")
face(blink_left:stop): user.stop_left_eye_closed_cron("left")

gamepad(east:down): user.gamepad_east_down()
gamepad(east:up): key("right:up")

parrot(hum:repeat): user.noise_start("up")
parrot(hum:stop): user.noise_stop("up", 300)

parrot(fff:repeat): user.noise_start("down")
parrot(fff:stop): user.noise_stop("down", 400)