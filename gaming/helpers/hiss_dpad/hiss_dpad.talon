user.hiss_dpad_active: yes
#mode: user.game
-

parrot(hum:repeat): key("up:down")
parrot(hum:stop): key("up:up")

parrot(shh:repeat): user.noise_start("down")
parrot(shh:stop): user.noise_stop("down")

parrot(fff:repeat): user.noise_start("left")
parrot(fff:stop): user.noise_stop("left")

parrot(vrr:repeat): user.noise_start("right")
parrot(vrr:stop): user.noise_stop("right")
