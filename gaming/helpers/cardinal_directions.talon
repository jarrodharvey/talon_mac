tag: user.cardinal_directions
mode: user.game 
-

# Cardinal directions
^{user.cardinal_direction}$: user.diagonal(cardinal_direction, cardinal_direction, 0, "True") 
^{user.cardinal_direction} <number>$: user.diagonal(cardinal_direction, cardinal_direction, number, "False") 

# Other cardinal directions
^(northeast) [hold]$: user.diagonal("up", "right", 0, "True") 
^(southeast | sex | dex | texts | solace | no fast | selfish) [hold]$: user.diagonal("right", "down", 0, "True") 
^(northwest | now | no) [hold]$: user.diagonal("up", "left", 0, "True")
^(southwest | swish | swiss | switch | bush) [hold]$: user.diagonal("left", "down", 0, "True")

^(northeast) <number>$: user.diagonal("up", "right", number, "False") 
^(southeast | sex | texts | solace) <number>$: user.diagonal("right", "down", number, "False") 
^(northwest | now | new) <number>$: user.diagonal("up", "left", number, "False")
^(southwest | swish | switch) <number>$: user.diagonal("left", "down", number, "False")

^sector$: user.diagonal("right", "down", 2, "False") 
^swish tor$: user.diagonal("down", "left", 2, "False") 
^sex full$: user.diagonal("down", "right", 4, "False") 
^vex wife$: user.diagonal("up", "right", 5, "False") 
^not true$: user.diagonal("up", "left", 2, "False") 
^now full$: user.diagonal("up", "left", 4, "False") 
^swish full$: user.diagonal("down", "left", 4, "False") 
^vector$: user.diagonal("up", "right", 2, "False") 
^next her$: user.diagonal("up", "right", 2, "False") 
^next full$: user.diagonal("up", "right", 4, "False") 
^noite$: user.diagonal("left", "up", 2, "False") 
^sector$: user.diagonal("down", "right", 2, "False") 
^now true$: user.diagonal("up", "left", 2, "False") 
^dexter$: user.diagonal("up", "right", 2, "False") 
^six three$: user.diagonal("down", "right", 3, "False") 
^softer$: user.diagonal("down", "down", 2, "False") 
^south want$: user.diagonal("down", "down", 1, "False") 
^waster$: user.diagonal("left", "left", 2, "False") 
^(this true | ester)$: user.diagonal("right", "right", 2, "False") 