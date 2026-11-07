# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is Jarrod's personal Talon voice control codebase — the `jarrod/` git repository, which lives inside the broader `~/.talon/user/` Talon configuration directory. It implements a sophisticated multi-modal voice control system focused on gaming automation and accessibility, and integrates with several third-party Talon extensions installed alongside it.

This file lives at `jarrod/CLAUDE.md` (tracked in git) and is symlinked from `~/.talon/user/CLAUDE.md` so Claude Code auto-loads it at session start.

### Porting to a new machine

After cloning this repo into `~/.talon/user/jarrod/`, recreate the symlink so Claude Code finds it:

```bash
ln -s jarrod/CLAUDE.md ~/.talon/user/CLAUDE.md
```

### Directory Structure

This repo IS the `jarrod/` directory. The sibling directories under `~/.talon/user/` are third-party Talon extensions — read-only from this repo's perspective, but referenced by code here:

- **../community/** - Talon community base command set
- **../cursorless-talon/** - Advanced voice coding system
- **../rango-talon/** - Browser navigation system
- **../talon-ai-tools/** - AI integration tools
- **../talon-gaze-ocr/** - Eye tracking + OCR system (used by pathfinding)
- **../talon-hud/** - HUD interface system
- **../talon_ui_helper/** - UI helper tools
- **../flex-mouse-grid/** - Advanced mouse grid system
- **../screen-spots/** - Screen spot clicking system
- **../betterinput/** - Versatile input actions library (distinct from the in-repo BetterInput pattern in `gaming/helpers/gaming.py`)
- **../cursorless-settings/** - Settings for cursorless integration
- **../ui_elements/** - UI component definitions
- **../face_tester/** - Eye/face tracking testing utilities

## Memories

### Screenshot Context
- Whenever I say that I sent you a screenshot or took a screenshot, I am referring to this directory: jarrod/claude_helpers/screenshots

### Talon Development
- Whenever creating or modifying a talon file, check the logs for debug messages
- You can run commands against the talon repl using "echo 'TALON_COMMAND' | /Users/jarrod/.talon/bin/repl". Use this for testing
- Use the talon repl for testing
- Every time you create or modify a file check the logs to see the debug message and confirm whether you broke anything
- Every single time you create or modify a file check the talon logs for debug messages. every single time.

### Testing Game-Specific Changes (focus-aware)
- Jarrod has the terminal in the foreground while talking to Claude Code, but the game is usually running in the background. A plain REPL test of a game change runs against the terminal, not the game.
- For any change specific to a game (`gaming/games/<game>.talon` or helpers used by that game), test with:
  ```bash
  claude_helpers/game_test.sh gaming/games/<game>.talon '<repl command>' [--wait SECS] [--screenshot] [--mimic]
  ```
  It reads the file's context header (`app:`/`title:`), checks that a matching window is running, focuses it, runs the command, waits `--wait` seconds (default 1), optionally screenshots, then **always** refocuses the terminal and tails the log.
- Use a longer `--wait` for cron-driven actions (repeat buttons, pathfinding), because they need the game focused while they run.
- Prefer direct `actions.user.*` calls. Use `--mimic` only to test a voice binding via `mimic(...)`: it temporarily switches to `user.game` mode and restores the previous modes afterwards.
- Exit 2 = game not running. Exit 3 = a streaming app (Moonlight / NVidia GeForce NOW) is running but `user.active_manual_game` doesn't match the file's header, so a different game is live. In both cases nothing is focused. Fall back to the plain REPL only for focus-independent checks (action registration, syntax), and tell Jarrod the in-game test was skipped. Exit 1 = focus failed or the command raised an exception.
- For streaming apps, the game is identified by the `user.active_manual_game` scope (`storage["user.manual_game"]`, set via `user.set_manual_game`), compared against the header's `user.active_manual_game:` line.
- Implementation: `claude_helpers/game_focus.py` (actions `claude_game_status`, `claude_focus_game`, `claude_restore_focus`, `claude_enter_game_mode`, `claude_restore_modes`).

### Repository Management
- When I say to commit my changes, this applies to the `jarrod/` directory — the sibling directories are external Talon extensions and are not tracked here
- The git repo lives at `~/.talon/user/jarrod/`, not at `~/.talon/user/`. `cd` into `jarrod/` before running git commands

### CRITICAL: Grid Menu Navigation Ban
- **NEVER ATTEMPT GRID MENU NAVIGATION UNDER ANY CIRCUMSTANCES**
- **DO NOT** create menu detection systems, grid detection, row/column analysis, or any form of "smart" menu navigation
- **DO NOT** attempt to detect menu structure, menu bounds, or menu item positioning
- **DO NOT** try to convert coordinates to "menu steps" or discrete menu movements
- **REASON**: Grid menu navigation has been attempted twice and failed completely both times due to:
  - Variable row/column thresholds between games and menus
  - Unreliable OCR text positioning and filtering
  - Complex menu layouts that don't fit grid assumptions
  - Inconsistent menu item detection vs flavor text
- **INSTEAD**: Use direct coordinate-based navigation with proximity adjustments only
- **IF** menu navigation issues arise, adjust proximity thresholds, not navigation approach

### Python Development
- When using pip install you need to use pip from /Users/jarrod/.talon/bin
- Talon files (.talon) reload automatically when modified; Python files (.py) hot-reload in most cases
- Syntax errors in Python files will break the entire module - always check logs immediately

### Research and Learning
- When researching (for example going through a codebase to learn how something works) use gemini with gemini -p "prompt" and prompt gemini to provide you with the information/report/summary you are seeking.

## Architecture Overview

### Core Subsystems

**jarrod/** is organized into these main subsystems:

1. **Mode System** (`my_commands.py`) - Manages exclusive states: `user.game`, `dictation`, `command`
2. **Gaming Automation** (`gaming/`) - Main gaming voice control system
3. **Pathfinding** (`gaming/helpers/pathfinding/`) - OCR-guided menu navigation
4. **BetterInput** (`gaming/helpers/gaming.py`) - Complex time-aware input sequences
5. **Wink Handler** (`wink_handler.py`) - Facial expression-based controls
6. **Claude Helpers** (`claude_helpers/`) - Development utilities and testing
7. **Controlled Vocabularies** (`controlled_vocabularies/`) - Custom talon-list vocabularies (R, zsh)
8. **Languages** (`languages/`) - Language-specific extensions (e.g., mermaid)

### Key Architectural Patterns

**Action System**: All functionality exposed via Talon actions:
```python
@mod.action_class
class Actions:
    def my_action(param1: str):
        """Documented action callable from .talon files"""
```

**Mode/Tag System**:
- Modes are exclusive states (game/dictation/command)
- Tags enable feature sets dynamically via `ctx.tags = ["user.ocr_pathfinding_button"]`

**Storage/Scope**:
- `storage.set/get()` persists state across sessions
- `@mod.scope` provides computed variables to .talon files

**Cron Job Pattern**: Use global references to prevent duplicate jobs:
```python
global navigation_job
if navigation_job:
    cron.cancel(navigation_job)
navigation_job = cron.interval("500ms", callback)
```

**Talon File Structure**:
- `.talon` files define voice commands with match conditions at the top (app, mode, tags)
- Commands map spoken phrases to actions: `^command phrase$: action_call()`
- Settings are configured per-context in `settings():` blocks
- Tags are enabled per-context with `tag():` declarations

**Talonscript Capabilities**:
Voice command bodies use Talonscript, "a very limited subset of Python" with these features:

- **Variable assignment**: Create and assign local variables
  ```
  result = number_small * 5
  letter_defaulted = letter or "default"
  message = "The result is {result}"
  ```

- **Mathematical operations**: One operation per line only
  ```
  a = a + b
  a = a - b
  a = a * b
  a = a / b
  a = a % b
  ```

- **String interpolation**: Use `{variable_name}` in strings
  ```
  app.notify("Value is {result}")
  ```

- **Conditional logic**: `or` operator for null coalescing
  ```
  value = optional_param or "default_value"
  ```

- **Limitations**:
  - No complex expressions (must break into single operations per line)
  - Comments must be on their own line (no inline comments)
  - Cannot do: `result = (a + b) * c` (requires multiple lines)
  - Can do: `temp = a + b` then `result = temp * c`

### Critical Systems

**BetterInput Pattern** (`gaming/helpers/gaming.py`):
- Custom implementation of time-aware input sequences: `"key1 | 500ms | key2 | 2s | key3"`
- `calculate_betterinput_duration()` parses timing for conditional logic
- Used for games that can't queue inputs naturally
- Note: Different from the third-party `betterinput/` module at repository root

**Pathfinding** (`gaming/helpers/pathfinding/`):
- OCR-guided navigation to menu items by text
- Multi-algorithm fuzzy matching with disambiguation UI
- Loop detection with tiebreaker logic
- Navigation modes: unified/vertical/horizontal/grid
- Key settings in `pathfinding/core/settings.py`
- **Disambiguation mode**: When multiple matches found, numbered overlay appears; say number to select
- Fuzzy matching uses Jaro-Winkler and other algorithms with configurable threshold

**Template Matching** (`gaming/helpers/pathfinding/ocr/template_matching.py`):
- Game-specific cursors in `gaming/cursors/{game_name}/`
- Flexible matching handles visual variations
- Uses OpenCV template matching to locate cursor/highlight position

**Wink Handler** (`wink_handler.py`):
- Detects left/right eye winks via facial expressions
- Configurable per-game via `wink_button_left`/`wink_button_right` settings
- Includes cooldown mechanism to prevent double-triggers
- Distinguishes winks from blinks using timing delay

## Common Development Commands

### Testing and Debugging

**Test Talon commands via REPL**:
```bash
echo 'app.notify("test message")' | /Users/jarrod/.talon/bin/repl
```

**Check Talon logs** (CRITICAL - do this after EVERY file modification):
```bash
tail -f /Users/jarrod/.talon/talon.log
```

**Capture debug screenshot**:
```python
actions.user.capture_claude_screenshot()
# Saves to jarrod/claude_helpers/screenshots/
```

**Debug pathfinding state**:
```bash
# Via REPL
echo 'actions.user.debug_pathfinding_state()' | /Users/jarrod/.talon/bin/repl

# Via voice command in game (if configured)
# "debug path"
```

### Development Workflow

1. Modify .talon or .py file
2. **IMMEDIATELY check logs**: `tail -20 /Users/jarrod/.talon/talon.log`
3. Look for syntax errors, import failures, or debug messages
4. Test via REPL or voice command
5. Check logs again for runtime errors

### Package Installation

**Always use Talon's pip**:
```bash
/Users/jarrod/.talon/bin/pip install package-name
```

### Game Development

**Adding a new game**:
1. Create `gaming/games/{game_name}.talon`
2. Add cursor templates to `gaming/cursors/{game_name}/`
3. Configure pathfinding settings in game's .talon file
4. Test navigation and adjust proximity thresholds

**Common game settings to tune**:
- `highlight_proximity_x/y` - arrival detection distance (smaller = more precise)
- `navigation_mode` - navigation strategy: unified/vertical/horizontal/grid
- `game_action_button` - confirmation button (e.g., "space", "enter")
- `cursor_directory` - path to game-specific cursor templates
- `uses_pathfinding` - enable OCR pathfinding vs simple click
- `uses_wasd` - use WASD vs arrow keys for navigation
- `navigation_interval` - milliseconds between navigation steps
- `default_action_button_count` - how many times to press action button
- `wink_button_left/right` - map winks to buttons (e.g., "space", "rmb")

### Common Voice Command Patterns

**Game .talon files** typically include these command categories:

1. **Parrot/noise handlers**: `parrot(click):`, `parrot(tch):` for quick actions
2. **Movement speed**: `^walk$`, `^sprint$`, `^jog$` - adjust repeat_button_speed
3. **Dialogue advancement**: `^dialogue$`, `^mash$` - automated button pressing
4. **Dynamic navigation**: `^go <user.prose>$` - OCR-based menu navigation
5. **Game-specific macros**: Multi-step sequences with timing (e.g., `^save game$`)
6. **Debug commands**: `^debug text$`, `^debug cursor$`, `^debug path$`

**Command syntax**:
- `^exact phrase$` - exact match with anchors
- `<user.prose>` - capture any spoken text for OCR navigation
- `<number>` - capture number parameter
- `[optional]` - optional phrase component
- `(option one | option two)` - alternatives

## File Structure

**Core files**:
- `jarrod/my_commands.py` - Mode switching system
- `jarrod/gaming/helpers/gaming.py` - ~945 lines of game actions (CRITICAL)
- `jarrod/gaming/helpers/pathfinding/core/navigation.py` - Navigation engine
- `jarrod/gaming/helpers/noise_handler.py` - Noise-based input handling
- `jarrod/gaming/helpers/repeat_keypress.py` - Keypress repetition system
- `jarrod/wink_handler.py` - Facial expression system

**Gaming data directories**:
- `jarrod/gaming/cursors/{game_name}/` - Template matching cursor images per game
- `jarrod/gaming/images_to_click/` - Clickable UI element templates (62+ game subdirs)
- `jarrod/gaming/game_disambiguation/` - Disambiguation UI word lists (.talon-list files)
- `jarrod/gaming/grid_cursors/` - Grid-based cursor templates

**Game implementations**:
- 20 games in `jarrod/gaming/games/*.talon` (see chained_echoes.talon for reference implementation)

**Third-party extensions** (read-only):
- All other top-level directories are external Talon packages
- community/ - Base Talon command set
- talon-gaze-ocr/ - OCR system used by pathfinding
- cursorless-talon/ - Advanced voice coding (not gaming-related)

### Commonly Used Actions

**From gaming.py** (callable in .talon files):
- `user.set_repeat_button(key, interval)` - Repeatedly press key at interval
- `user.press_key_x_times(key, count, interval)` - Press key N times with delay
- `user.game_stop()` - Cancel all active gaming cron jobs
- `user.navigate_to_word(text)` - OCR pathfinding to menu item
- `user.click_image(filename)` - Click on image template match
- `user.conditional_image_button_press(key, image, timeout, final_press)` - Press key until image appears
- `user.set_global_variable(var_name, value)` - Runtime settings adjustment
- `user.super_click(duration)` - Long mouse press for drag operations

## Troubleshooting

**Pathfinding not working**:
1. Check cursor templates exist in `gaming/cursors/{game_name}/`
2. Verify `cursor_directory` setting matches folder name
3. Adjust `highlight_proximity_x/y` - too tight causes navigation loops
4. Check OCR is detecting text: `actions.user.debug_all_text_coordinates()`
5. Ensure `uses_pathfinding` is true in game's settings

**Navigation loops/oscillation**:
- Increase `highlight_proximity_x/y` values
- Check `position_stability_threshold` (should be 2x navigation_interval)
- Verify navigation_mode is appropriate for menu layout

**Commands not working**:
1. Check Talon logs immediately: `tail -20 /Users/jarrod/.talon/talon.log`
2. Verify mode is correct (game/dictation/command): check mode indicator
3. Ensure tags are enabled for the command's requirements
4. Test in REPL to isolate voice vs code issues

**Cron jobs not stopping**:
- Always call `user.game_stop()` before starting new jobs
- Check global variable is being set/cancelled correctly
- Look for job references in gaming.py global variables section

## Important Constraints

- **NO pip install without full path** - use `/Users/jarrod/.talon/bin/pip`
- **NO hard-coded species names** - applies to phylogeny work (90k species in DB)
- **NO graceful fallbacks during dev** - explicit errors preferred
- **CHECK LOGS AFTER EVERY CHANGE** - catches syntax/import errors immediately
- **NO modifications to third-party directories** - only work in jarrod/