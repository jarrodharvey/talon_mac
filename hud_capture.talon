# Keep the Talon HUD (event log etc.) out of screen captures so OCR and image
# matching never see it, while it stays visible on screen. Requires Talon beta.
# Recommended by talon-gaze-ocr's README.
settings():
    user.talon_hud_allows_capture = false
