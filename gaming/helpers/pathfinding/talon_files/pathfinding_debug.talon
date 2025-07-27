# Test file for cube functionality
# Commands for testing the cube navigation system

^show cubes$: user.show_cubes()
^hide cubes$: user.hide_cubes()
^go cube <number>$: user.navigate_to_cube(number)
^cube <number>$: user.navigate_to_cube(number)

# Quick test commands
^test cube zero$: user.navigate_to_cube(0)
^test cube one$: user.navigate_to_cube(1)
^test cube two$: user.navigate_to_cube(2)