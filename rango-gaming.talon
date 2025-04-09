app: Chrome
and tag: user.rango_direct_clicking
mode: user.game
-
^<user.rango_target>$:
    user.game_stop()
    user.rango_command_with_target("directClickElement", rango_target)