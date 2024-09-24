app: Chrome
and tag: user.rango_direct_clicking
mode: user.game
-
^<user.rango_target>$:
    user.game_stop()
    user.rango_command_with_target("directClickElement", rango_target)

# Hover
^hover <user.rango_target>$:
  user.rango_command_with_target("hoverElement", rango_target)
^dismiss$: user.rango_command_without_target("unhoverAll")

^opponent$: user.move_to_spot("showdown opponents") 
^myself$: user.move_to_spot("showdown myself") 
^away$: user.move_to_spot("showdown away") 