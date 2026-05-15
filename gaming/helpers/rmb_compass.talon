tag: user.rmb_compass_directions
mode: user.game
-

^north$:               user.rmb_compass_move("north")
^south$:               user.rmb_compass_move("south")
^taste$:                user.rmb_compass_move("east")
^west$:                user.rmb_compass_move("west")
^(northeast | next)$:  user.rmb_compass_move("northeast")
^(southeast | socks)$: user.rmb_compass_move("southeast")
^(northwest | now)$:   user.rmb_compass_move("northwest")
^(southwest | swish)$: user.rmb_compass_move("southwest")

^north <number>$:               user.rmb_compass_move("north", number)
^south <number>$:               user.rmb_compass_move("south", number)
^taste <number>$:                user.rmb_compass_move("east", number)
^west <number>$:                user.rmb_compass_move("west", number)
^(northeast | next) <number>$:  user.rmb_compass_move("northeast", number)
^(southeast | socks) <number>$: user.rmb_compass_move("southeast", number)
^(northwest | now) <number>$:   user.rmb_compass_move("northwest", number)
^(southwest | swish) <number>$: user.rmb_compass_move("southwest", number)
