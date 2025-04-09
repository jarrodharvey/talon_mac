tag: user.ocr_click_button
mode: user.game
-

^<user.timestamped_prose>$:
    user.move_cursor_to_word(timestamped_prose)
    user.super_click()