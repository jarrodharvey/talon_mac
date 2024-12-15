from talon import Module, actions, cron

mod = Module()

# up: 
    # x range: -0.085 to -0.095
    # y range: -0.120 to -0.130
# down:
    # x range: -0.055 to -0.065
    # y range: -0.120 to -0.130
# left:
    # x range: -0.110 to -0.120
    # y range: -0.140 to -0.150
# right:
    # x range: -0.010 to -0.020
    # y range: -0.220 to -0.230

@mod.action_class
class Actions:
    def print_gaze_direction(x: float, y: float):
        """Print the gaze direction"""
        if y < -0.120:
            if x < -0.085:
                print("up")
            elif x > -0.055:
                print("down")
        elif x < -0.110:
            print("left")
        elif x > -0.010:    
            print("right")
