# Bare number chooses on the OCR disambiguation overlay, unless the game sets
# user.ocr_disambiguation_require_choose (e.g. it binds bare numbers to hotkeys).
mode: user.game
tag: user.gaze_ocr_disambiguation
and not tag: user.ocr_disambiguation_require_choose
-
^<number_small>$: user.choose_gaze_ocr_option(number_small)
