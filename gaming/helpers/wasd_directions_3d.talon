tag: user.wasd_directions_3d
mode: user.game 
-

^north$: user.diagonal_3d("w", "w")
^(south | self)$: user.diagonal_3d("s", "s")
^taste$: user.diagonal_3d("d", "d")
^west$: user.diagonal_3d("a", "a")

^(northeast | next)$: user.diagonal_3d("w", "d")
^(southeast | socks)$: user.diagonal_3d("s", "d")
^(northwest | now)$: user.diagonal_3d("w", "a")
^(southwest | swish)$: user.diagonal_3d("s", "a")

^up$: 
    user.game_stop()
    key("w:down")
^down$: 
    user.game_stop()
    key("s:down")
^left$:
    user.game_stop()
    key("a:down")
^right$:
    user.game_stop()
    key("d:down")