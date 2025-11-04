tag: user.wasd_directions
mode: user.game 
-

^north$: user.diagonal("w", "w", 0, "True")
^(south | self)$: user.diagonal("s", "s", 0, "True")
^taste$: user.diagonal("d", "d", 0, "True")
^west$: user.diagonal("a", "a", 0, "True")

^next$: user.diagonal("w", "d", 0, "True")
^socks$: user.diagonal("s", "d", 0, "True")
^now$: user.diagonal("w", "a", 0, "True")
^swish$: user.diagonal("s", "a", 0, "True")