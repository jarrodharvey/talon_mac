tag: user.cardinal_directions
mode: user.game 
-

# Cardinal directions
^{user.cardinal_direction}$: user.diagonal(cardinal_direction, cardinal_direction, 0, "True") 
^{user.cardinal_direction} <number>$: user.diagonal(cardinal_direction, cardinal_direction, number, "False") 

# Other cardinal directions
^(northeast | next) [hold]$: user.diagonal("up", "right", 0, "True") 
^(southeast | socks) [hold]$: user.diagonal("right", "down", 0, "True") 
^(northwest | now) [hold]$: user.diagonal("up", "left", 0, "True")
^(southwest | swish) [hold]$: user.diagonal("left", "down", 0, "True")

^(northeast | next) <number>$: user.diagonal("up", "right", number, "False") 
^(southeast | socks) <number>$: user.diagonal("right", "down", number, "False") 
^(northwest | now) <number>$: user.diagonal("up", "left", number, "False")
^(southwest | swish) <number>$: user.diagonal("left", "down", number, "False")