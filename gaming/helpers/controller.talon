gamepad(south:down): 
    user.switch_microphone("Razer Kraken X USB")
    user.set_input_volume(0)
    user.game_mode()

gamepad(south:up): 
    user.set_input_volume(75)
    user.game_stop()
    mode.disable("user.game")
    speech.disable()

gamepad(east:down):
    button_to_press = user.get_value_from_json_file("/Users/jarrod/.talon/user/jarrod/gaming/helpers/button_interval.json", "button")
    interval_in_seconds = user.get_value_from_json_file("/Users/jarrod/.talon/user/jarrod/gaming/helpers/button_interval.json", "interval")
    user.start_keypress(button_to_press, interval_in_seconds)
    user.hud_publish_content('Pressing {button_to_press} every {interval_in_seconds} seconds', 'example', 'Pressing button')

gamepad(east:up): user.game_stop()

gamepad(west:down): 
    user.game_stop()
    user.game_tracker_on()
gamepad(west:up): 
    user.game_stop()
    user.game_tracker_off()