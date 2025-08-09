tag: user.ocr_pathfinding_button
mode: user.game
-

# Disambiguation commands (processed first)
[choose] <number_small>: user.choose_pathfinding_option(number_small)
choose to: user.choose_pathfinding_option(2)
numbers hide: user.hide_pathfinding_options()

# General navigation (processed last) - but exclude disambiguation patterns
<user.timestamped_prose>:
    user.navigate_to_phrase_with_action(timestamped_prose)
