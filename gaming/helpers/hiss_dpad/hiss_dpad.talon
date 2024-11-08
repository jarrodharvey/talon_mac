user.hiss_dpad_active: yes
mode: user.game
-

parrot(hum:repeat): user.noise_start("up")
parrot(hum:stop): user.noise_stop("up")

parrot(shh:repeat): user.noise_start("down")
parrot(shh:stop): user.noise_stop("down")

parrot(fff:repeat): user.noise_start("left")
parrot(fff:stop): user.noise_stop("left")

parrot(vrr:repeat): user.noise_start("right")
parrot(vrr:stop): user.noise_stop("right")

parrot(click): user.take_step("up")

parrot(tch): user.take_step("down")

parrot(raspberry): user.take_step("left")

parrot(kiss): user.take_step("right")