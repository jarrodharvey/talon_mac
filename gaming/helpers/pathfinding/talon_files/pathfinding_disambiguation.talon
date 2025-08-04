mode: user.gaming_pathfinding_disambiguation
-
choose <number_small>: user.choose_pathfinding_option(number_small)
# Handle frequent misrecognition
choose to: user.choose_pathfinding_option(2)
numbers hide: user.hide_pathfinding_options()

# Debug commands (can be removed later)
debug disambiguation: user.get_disambiguation_state()