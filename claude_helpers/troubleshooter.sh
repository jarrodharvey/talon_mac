#!/bin/bash
# Robust Moonlight boxes debugging script with multiple focus attempts

echo "🔧 Testing Moonlight boxes with robust window switching..."

# Start HUD notification
echo 'actions.user.hud_publish_content("🔧 Testing: Attempting to focus Moonlight")' | ~/.talon/bin/repl

# Try multiple approaches to focus Moonlight
echo "Attempting to focus Moonlight (try 1)..."
echo 'actions.user.switcher_focus("Moonlight")' | ~/.talon/bin/repl
sleep 1

echo "Checking if focus worked..."
echo 'current_app = ui.active_window().app.name if ui.active_window() else "unknown"; print(f"Current app: {current_app}")' | ~/.talon/bin/repl
sleep 1

echo "Attempting to focus Moonlight (try 2)..."
echo 'try: actions.user.switcher_focus("Moonlight")
except: print("Focus attempt 2 failed")' | ~/.talon/bin/repl
sleep 1

echo "Trying alternative method..."
echo 'try: 
    import ui
    moonlight_apps = [app for app in ui.apps() if "moonlight" in app.name.lower()]
    if moonlight_apps:
        moonlight_apps[0].focus()
        print(f"Focused via direct app focus: {moonlight_apps[0].name}")
    else:
        print("No Moonlight app found")
except Exception as e:
    print(f"Direct focus failed: {e}")' | ~/.talon/bin/repl
sleep 2

# Check final state
echo "Final app check..."
echo 'final_app = ui.active_window().app.name if ui.active_window() else "unknown"; print(f"Final app: {final_app}")' | ~/.talon/bin/repl

# Update HUD 
echo 'actions.user.hud_publish_content("🔧 Testing: Taking before screenshot")' | ~/.talon/bin/repl

# Take screenshot before boxes
echo "Taking screenshot before boxes..."
echo 'import subprocess; subprocess.run(["screencapture", "/tmp/moonlight_before_robust.png"]); print("Before screenshot saved")' | ~/.talon/bin/repl

# Update HUD status
echo 'actions.user.hud_publish_content("🔧 Testing: Showing boxes overlay")' | ~/.talon/bin/repl

# Show boxes/cubes
echo "Showing boxes..."
echo 'actions.user.show_cubes()' | ~/.talon/bin/repl

# Wait for boxes to appear
sleep 3

# Take screenshot with boxes
echo "Taking screenshot with boxes..."
echo 'import subprocess; subprocess.run(["screencapture", "/tmp/moonlight_with_boxes_robust.png"]); print("Boxes screenshot saved")' | ~/.talon/bin/repl

# Hide the cubes
echo "Hiding cubes..."
echo 'actions.user.hide_cubes()' | ~/.talon/bin/repl

# Wait for cubes to disappear
sleep 1

# Take final screenshot after cleanup
echo "Taking final cleanup screenshot..."
echo 'import subprocess; subprocess.run(["screencapture", "/tmp/moonlight_after_cleanup_robust.png"]); print("Cleanup screenshot saved")' | ~/.talon/bin/repl

# Clear HUD notification
echo "Clearing HUD..."
echo 'try: actions.user.hud_clear_all()
except: 
    try: actions.user.hud_clear()
    except: 
        try: actions.user.hud_publish_content("")
        except: pass' | ~/.talon/bin/repl

echo "✅ Robust test complete - screenshots:"
echo "  Before: /tmp/moonlight_before_robust.png"
echo "  With boxes: /tmp/moonlight_with_boxes_robust.png"  
echo "  After cleanup: /tmp/moonlight_after_cleanup_robust.png"