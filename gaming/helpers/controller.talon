gamepad(south:down): 
    user.game_mode()
    user.daily_exercise_reminder()
    # Set the discord microphone volume to zero
    #user.switch_microphone("Razer Kraken X USB")
    #user.set_input_volume(0)
    # Enable the talon microphone
    sound.set_microphone("External Microphone")

gamepad(south:up): 
    user.game_stop()
    mode.disable("user.game")
    speech.disable()
    # Set the discord microphone volume to 100
    #user.switch_microphone("Razer Kraken X USB")
    #user.set_input_volume(30)
    # Disable the talon microphone so that it won't pick up on utterances
    #sound.set_microphone("None")

gamepad(east:down): user.gamepad_east_down()

gamepad(east:up): user.game_stop()

gamepad(west:down): 
    user.game_stop()
    user.game_tracker_on()
gamepad(west:up): 
    user.game_tracker_off()

gamepad(r2:down): user.enable_ocr_click_button()
gamepad(r2:up): user.disable_ocr_click_button()