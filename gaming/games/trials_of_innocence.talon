user.active_manual_game: trials of innocence
mode: user.game
not mode: user.gaze_ocr_disambiguation
app: moonlight
-
settings():
    key_wait = 40

^dialogue$: user.set_repeat_button("space", 6)
^speed$: user.set_repeat_button("space", 1)
^slideshow$: 
    user.click_image("innocence_next.png")
    user.set_repeat_button("click", 3)

parrot(click): mouse_click(0)
parrot(tch): user.click_image("innocence_exit.png")

^menu$: key("escape")

^previous$: user.click_image("innocence_previous.png")
^next$: user.click_image("innocence_next.png")

^back$: 
    user.click_image("innocence_exit.png")
    user.click_image("innocence_exit.png")

^{user.jarrod.gaming.helpers.word_numbers.list}$: user.game_click_spot("innocence {user.jarrod.gaming.helpers.word_numbers.list}")
^fuck$: user.game_click_spot("fuck off")

^review {user.jarrod.gaming.helpers.word_numbers.list}$: 
    user.game_click_spot("innocence {user.jarrod.gaming.helpers.word_numbers.list}")
    sleep(1s)
    user.game_click_spot("innocence review")

^review$: user.game_click_spot("innocence review")

^save game$: 
    key("escape")
    sleep(1s)
    user.click_image("innocence_save.png")
    sleep(1s)
    mouse_click(0)
    sleep(1s)
    user.click_image("innocence_confirm.png")
    sleep(1s)
    user.click_image("innocence_exit.png")

^load game$: 
    key("escape")
    sleep(1s)
    user.click_image("innocence_load.png")
    sleep(1s)
    mouse_click(0)
    sleep(1s)
    user.click_image("innocence_confirm.png")
    sleep(1s)
    user.click_image("innocence_exit.png")

^dub <user.timestamped_prose>$:
    user.disconnect_ocr_eye_tracker()
    user.move_cursor_to_word(timestamped_prose)
    user.connect_ocr_eye_tracker()
    user.super_click()
    sleep(1s)
    user.super_click()

^touch$: mouse_click(0)