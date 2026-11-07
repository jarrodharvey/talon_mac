# Disambiguation overlay commands while R1 (OCR click) is held.
# The extra tag makes this more specific than the prose catch-all in ocr_click_button.talon.
mode: user.game
tag: user.gaze_ocr_disambiguation
and tag: user.ocr_click_button
-
choose <number_small>: user.choose_gaze_ocr_option(number_small)
choose to: user.choose_gaze_ocr_option(2)
numbers hide: user.hide_gaze_ocr_options()
