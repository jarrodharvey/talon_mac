gamepad(south:down): 
    user.game_mode()
    user.daily_exercise_reminder()
    # Make sure that the correct microphone is selected for setting the volume to 0
    user.switch_microphone("Razer Kraken X USB")
    user.set_input_volume(0)

gamepad(south:up): 
    user.game_stop()
    mode.disable("user.game")
    speech.disable()
    user.set_input_volume(75)

gamepad(east:down): user.gamepad_east_down()

gamepad(east:up): user.game_stop()

gamepad(west:down): 
    user.game_stop()
    user.game_tracker_on()
gamepad(west:up): 
    user.game_stop()
    user.game_tracker_off()

gamepad(r2:down): user.enable_ocr_click_button()
gamepad(r2:up): user.disable_ocr_click_button()