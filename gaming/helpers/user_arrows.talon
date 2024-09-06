tag: user.user_arrows
mode: user.game
-

(hold | pulled | bold | old | home | all | bolt | hot) <user.arrow_keys>:
    key("left:up")
    key("right:up")
    key("up:up")
    key("down:up")
    user.hold_arrow(arrow_keys) 

(stop | gop): user.game_stop()

<user.arrow_keys>:
    user.game_stop()
    user.walk(arrow_keys)

<user.arrow_keys> twice:
    user.walk(arrow_keys)
    repeat(1)

<user.arrow_keys> free:
    user.walk(arrow_keys)
    repeat(2)

<user.arrow_keys> <number_small>:
    user.game_stop()
    user.walk(arrow_keys)
    repeat(number_small - 1)

<user.arrow_keys> in:
    user.walk(arrow_keys)
    repeat(7)

(dope | dot): key("down")

# homophones for arrow commands
opt free:
    user.walk("up")
    repeat(3)
(downfall | stand for):
    user.walk("down")
    repeat(3) 
apter:
    user.walk("up")
    repeat(2)
<user.arrow_keys> fall: 
    user.walk(arrow_keys)
    repeat(4)
<user.arrow_keys> to:    
    user.walk(arrow_keys)
    repeat(1)
^(lefter | left her)$:
    user.walk("left")
    repeat(2)
caret: user.walk("right")
rightful:
    user.walk("right")
    repeat(3)
right it: 
    user.walk("right")
    repeat(8)
not for:    
    user.walk("left")
    repeat(4)
don't ice:
    user.walk("down")
    user.walk("down")
wolfed: user.walk("left")
rut: user.walk("right")
girlish: user.walk("right")

# Homophones for taking a certain number of steps
(rat) <number_small>:
    user.walk("right")
    repeat(number_small)
<user.arrow_keys> for:
    user.walk(arrow_keys)
    repeat(3)
of the <user.number_small>:
    user.walk(arrow_keys)
    repeat(number_small - 1)
a free:
    user.walk("up")
    repeat(2)
<user.arrow_keys> fine:
    user.walk(arrow_keys)
    repeat(5)

gop: key("up")

<user.arrow_keys> full:
    user.walk(arrow_keys)
    repeat(3)

(rut | write): key("right")

[move] <user.arrow_keys>: key(arrow_keys)

(big | leak | back | buck | pack | thank | bit | he | pick) <user.arrow_keys>:
    user.walk(arrow_keys)
    repeat(11)

be (grat | grit): 
    user.walk(arrow_keys)
    repeat(11)

rotor:
    user.walk("right")
    repeat(2)

(donate | down it):
    user.walk("down")
    repeat(8)

wright twice:
    user.walk("right")
    repeat(1)

spin <user.arrow_keys>: 
    key(arrow_keys)
    key(arrow_keys)