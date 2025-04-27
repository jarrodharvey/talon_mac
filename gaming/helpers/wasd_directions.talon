tag: user.wasd_directions
mode: user.game 
-

^north$: user.diagonal("w", "w", 0, "True")
^south$: user.diagonal("s", "s", 0, "True")
^east$: user.diagonal("d", "d", 0, "True")
^west$: user.diagonal("a", "a", 0, "True")

^northeast$: user.diagonal("w", "d", 0, "True")
^southeast$: user.diagonal("s", "d", 0, "True")
^northwest$: user.diagonal("w", "a", 0, "True")
^southwest$: user.diagonal("s", "a", 0, "True")