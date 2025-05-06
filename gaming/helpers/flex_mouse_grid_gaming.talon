tag: user.flex_mouse_grid_showing
mode: user.game
-

# Coordinate input
<user.letter> <user.letter> <number>:
    # Say a letter to choose a row, say a second letter to choose a column, and say a number to
    # choose the numbered block. Example: "air bat 2"
    user.flex_grid_input_partial(number)
    user.flex_grid_input_partial(letter_1)
    user.flex_grid_input_partial(letter_2)


<user.letter> <user.letter>:
    # Using the currently selected number block, say a letter to choose a row and say a second
    # letter to choose a column. Example: "bat cap"
    user.flex_grid_input_partial(letter_1)
    user.flex_grid_input_partial(letter_2)


<number> <user.letter> <user.letter>:
    # Say a number to select a number block, say a letter to select a row, and say a second leter to
    # select a column. Example: "1 bat cap"
    user.flex_grid_input_partial(number)
    user.flex_grid_input_partial(letter_1)
    user.flex_grid_input_partial(letter_2)

<number> <user.letter>:
    user.flex_grid_input_partial(number)
    user.flex_grid_input_partial(letter)

^<number>$:
    # Say a number to select a number block.
    user.flex_grid_input_partial(number)

^row <user.letter>$:
    # If you already have a row selected, saying 'row' followed by a letter will select a new
    # horizontal row.
    user.flex_grid_input_horizontal(letter)

^<user.letter>$:
    # Input a single letter. Depending on where you are in the command sequence it will select either
    # a row or a column.
    user.flex_grid_input_partial(letter)

# Allows typing letters while the flex grid is showing. Example: "press air bat cap"
^press <user.keys>$:
    key(keys)

# Configuration
# Change the overlay pattern to a checkerboard pattern.
grid checker: user.flex_grid_checkers()

# Change the overlay pattern to a pattern where it is overlaid with frames.
grid frame: user.flex_grid_frame()

# Provides onscreen phonetic alphabet in rows and columns to make it so one does not have to
# remember the talon phonetic alphabet
grid phonetic: user.flex_grid_phonetic()

# Change the overlay pattern to overlay the screen with every possible number-letter-letter combination
grid full: user.flex_grid_full()

# Make the grid blocks larger.
grid bigger: user.flex_grid_adjust_size(5)
grid bigger bump: user.flex_grid_adjust_size(1)

# Make the grib blocks smaller.
grid smaller: user.flex_grid_adjust_size(-5)
grid smaller bump: user.flex_grid_adjust_size(-1)

# Make the small letter labels more visible.
letters darker: user.flex_grid_adjust_label_transparency(50)
letters darker bump: user.flex_grid_adjust_label_transparency(10)

# Make the small letter labels less visible.
letters lighter: user.flex_grid_adjust_label_transparency(-50)
letters lighter bump: user.flex_grid_adjust_label_transparency(-10)

# Make the large number blocks more visible.
background darker: user.flex_grid_adjust_bg_transparency(20)
background darker bump: user.flex_grid_adjust_bg_transparency(4)

# Make the large number blocks less visible.
background lighter: user.flex_grid_adjust_bg_transparency(-20)
background lighter bump: user.flex_grid_adjust_bg_transparency(-4)

# Show rulers around outside of grid
rulers switch: user.flex_grid_rulers_toggle()
