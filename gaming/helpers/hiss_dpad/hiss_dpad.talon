user.hiss_dpad_active: yes
#mode: user.game
-

parrot(hum:repeat): user.noise_start("up")
parrot(hum:stop): user.noise_stop("up")

parrot(shh:repeat): user.noise_start("down")
parrot(shh:stop): user.noise_stop("down")

parrot(fff:repeat): user.noise_start("left")
parrot(fff:stop): user.noise_stop("left")

parrot(vrr:repeat): user.noise_start("right")
parrot(vrr:stop): user.noise_stop("right")

###

# parrot(hum:repeat): key("up:down")
# parrot(hum:stop): key("up:up")

# parrot(shh:repeat): key("down:down")
# parrot(shh:stop): key("down:up")

# parrot(fff:repeat): key("left:down")
# parrot(fff:stop): key("left:up")

# parrot(vrr:repeat): key("right:down")
# parrot(vrr:stop): key("right:up")
