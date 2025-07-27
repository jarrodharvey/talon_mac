tag: user.pathfinding_cubes
-

# Cube appearance settings - using word values that map to hex codes
cube color red:
    user.set_cube_background_color("ff0000")

cube color green:
    user.set_cube_background_color("00ff00")

cube color blue:
    user.set_cube_background_color("0000ff")

cube color light blue:
    user.set_cube_background_color("87ceeb")

cube color white:
    user.set_cube_background_color("ffffff")

cube color black:
    user.set_cube_background_color("000000")

cube border red:
    user.set_cube_stroke_color("ff0000")

cube border green:
    user.set_cube_stroke_color("00ff00") 

cube border blue:
    user.set_cube_stroke_color("0000ff")

cube border dark blue:
    user.set_cube_stroke_color("4682b4")

cube border black:
    user.set_cube_stroke_color("000000")

cube text red:
    user.set_cube_text_color("ff0000")

cube text green:
    user.set_cube_text_color("00ff00")

cube text blue:
    user.set_cube_text_color("0000ff")

cube text black:
    user.set_cube_text_color("000000")

cube text white:
    user.set_cube_text_color("ffffff")

cube text background red:
    user.set_cube_text_background_color("ff0000")

cube text background green:
    user.set_cube_text_background_color("00ff00")

cube text background blue:
    user.set_cube_text_background_color("0000ff")

cube text background white:
    user.set_cube_text_background_color("ffffff")

cube text background black:
    user.set_cube_text_background_color("000000")

cube transparency <number>:
    user.set_cube_transparency(number)

cube text transparency <number>:
    user.set_cube_text_transparency(number)

cube border width <number>:
    user.set_cube_stroke_width(number)

cube text size <number>:
    user.set_cube_text_size(number)

cube font arial:
    user.set_cube_font("arial")

cube font helvetica:
    user.set_cube_font("helvetica")

cube font times:
    user.set_cube_font("times")

cube font courier:
    user.set_cube_font("courier")

# Cube filtering settings  
cube min width <number>:
    user.set_cube_min_width(number)

cube min height <number>:
    user.set_cube_min_height(number)

cube max count <number>:
    user.set_cube_max_count(number)

cube target offset <number>:
    user.set_cube_target_offset_x(number)

# Configuration commands
cube settings show:
    user.show_cube_settings()

cube settings reset:
    user.reset_cube_settings()

cube settings save:
    user.save_cube_settings()