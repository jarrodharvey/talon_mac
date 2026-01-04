mode: user.game
tag: user.panning
-

^west$: user.repeat_button_with_cron("a")
^taste$: user.repeat_button_with_cron("d")
^north$: user.repeat_button_with_cron("w")
^south$: user.repeat_button_with_cron("s")

# Diagonal panning
^next$: user.repeat_diagonal_with_cron("w", "d")
^socks$: user.repeat_diagonal_with_cron("s", "d")
^now$: user.repeat_diagonal_with_cron("w", "a")
^swish$: user.repeat_diagonal_with_cron("s", "a")