gamepad(south:down): 
    user.game_mode()
    user.daily_exercise_reminder()

gamepad(south:up): 
    user.hiss_dpad_off()
    user.game_stop()
    mode.disable("user.game")
    speech.disable()

gamepad(east:down): user.gamepad_east_down()

gamepad(east:up): user.game_stop()

gamepad(west:down): 
    user.game_stop()
    user.game_tracker_on()
gamepad(west:up): 
    user.game_stop()
    user.game_tracker_off()

gamepad(l1:down): 
    user.game_stop()
    user.hiss_dpad_on()
gamepad(l1:up): 
    user.game_stop()
    user.hiss_dpad_off()