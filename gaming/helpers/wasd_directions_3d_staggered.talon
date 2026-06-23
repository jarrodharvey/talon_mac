tag: user.wasd_directions_3d_staggered
mode: user.game 
-

^north$: user.diagonal_3d("w", "w", "yes")
^(south | self)$: user.diagonal_3d("s", "s", "yes")
^taste$: user.diagonal_3d("d", "d", "yes")
^west$: user.diagonal_3d("a", "a", "yes")

^(northeast | next)$: user.diagonal_3d("w", "d", "yes")
^(southeast | socks)$: user.diagonal_3d("s", "d", "yes")
^(northwest | now)$: user.diagonal_3d("w", "a", "yes")
^(southwest | swish)$: user.diagonal_3d("s", "a", "yes")