^personal email$: "jarrodharvey@gmail.com"

^fix <user.timestamped_prose_only>$:
    user.revise_text(timestamped_prose_only)

face(smile): print("you just smiled")

parrot(click): print("click")
parrot(tch): print("tch")

parrot(hum): user.noise_start("ctrl")
parrot(hum:stop): user.noise_stop("ctrl")