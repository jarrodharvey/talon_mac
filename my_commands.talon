face(smile): print("You just smiled!")
face(raise_eyebrows): print("You raised your eyebrows")
face(jaw_open): print("You just opened your mouth")
face(frown:stop): 
    print("You just frowned")

^personal email$: "jarrodharvey@gmail.com"

^fix <user.timestamped_prose_only>$:
    user.revise_text(timestamped_prose_only)

parrot(click): print("click")
parrot(tch): print("tch")