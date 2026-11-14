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

# Reads gaming/helpers/button_interval.json and acts on its action_type:
#   single_press - tap `button` once
#   hold         - hold `button` down until east is released
#   image        - click image template `button` every `interval` seconds
#   grinding     - run start_grinding (button, interval ms, battle_image, dir_hold, victory_image) while east is held
#   key (default) - press `button` every `interval` seconds, held for `key_hold` ms
# Releasing east (below) calls game_stop(), which cancels whatever was started.
gamepad(east:down): user.gamepad_east_down()

gamepad(east:up): user.game_stop()

gamepad(west:down):
    user.game_stop()
    user.game_tracker_on()
gamepad(west:up):
    user.game_tracker_off()

gamepad(r1:down): user.enable_ocr_click_button()
gamepad(r1:up): user.disable_ocr_click_button()