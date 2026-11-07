tag: user.ocr_click_button
and not tag: user.gaze_ocr_disambiguation
mode: user.game
-

# Disabled while the disambiguation overlay is showing, so "choose <n>" isn't swallowed as prose.
^<user.timestamped_prose>$: user.ocr_click_text(timestamped_prose)
