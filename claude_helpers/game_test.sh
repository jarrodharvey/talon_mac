#!/bin/bash
# Run a Talon REPL command with the game (per its .talon context header) in focus,
# then return focus to the terminal.
#
# Usage: game_test.sh <game.talon> '<repl command>' [--wait SECS] [--screenshot] [--mimic]
#
# Exit codes: 0 ok, 1 error, 2 game not running, 3 streaming app running a different
# game (user.active_manual_game mismatch). Nothing is focused for 2 or 3.

REPL="$HOME/.talon/bin/repl"
LOG="$HOME/.talon/talon.log"

usage() { echo "Usage: $0 <game.talon> '<repl command>' [--wait SECS] [--screenshot] [--mimic]" >&2; exit 1; }

[ $# -ge 2 ] || usage
TALON_FILE="$1"; CMD="$2"; shift 2
WAIT=1; SCREENSHOT=0; MIMIC=0
while [ $# -gt 0 ]; do
    case "$1" in
        --wait) WAIT="$2"; shift 2 ;;
        --screenshot) SCREENSHOT=1; shift ;;
        --mimic) MIMIC=1; shift ;;
        *) usage ;;
    esac
done

[ -f "$TALON_FILE" ] || { echo "No such file: $TALON_FILE" >&2; exit 1; }
TALON_FILE="$(cd "$(dirname "$TALON_FILE")" && pwd)/$(basename "$TALON_FILE")"

repl() { echo "$1" | "$REPL" 2>&1 | grep -v '^Talon REPL'; }
json_of() { grep '^CLAUDE_GAME_JSON:' | tail -1 | sed 's/^CLAUDE_GAME_JSON://'; }

# 1. Is the game running?
STATUS_OUT="$(repl "actions.user.claude_game_status(\"$TALON_FILE\")")"
STATUS="$(echo "$STATUS_OUT" | json_of)"
if [ -z "$STATUS" ]; then
    echo "Status check failed:"; echo "$STATUS_OUT"; exit 1
fi
echo "status: $STATUS"
if ! echo "$STATUS" | grep -q '"running": true'; then
    echo "GAME NOT RUNNING -> use plain REPL for focus-independent checks, or ask Jarrod to open it."
    exit 2
fi
if ! echo "$STATUS" | grep -q '"game_matches": true'; then
    echo "DIFFERENT GAME ACTIVE -> streaming app is running but user.active_manual_game doesn't match this file. Ask Jarrod to switch games."
    exit 3
fi

# 2. Always restore focus (and modes) on exit.
cleanup() {
    [ "$MIMIC" = 1 ] && repl "actions.user.claude_restore_modes()" | json_of | sed 's/^/modes: /'
    repl "actions.user.claude_restore_focus()" | sed 's/^CLAUDE_GAME_JSON:/restore: /'
    echo "----- talon.log (last 30) -----"
    tail -30 "$LOG"
}
trap cleanup EXIT

# 3. Focus the game.
FOCUS_OUT="$(repl "actions.user.claude_focus_game(\"$TALON_FILE\")")"
FOCUS="$(echo "$FOCUS_OUT" | json_of)"
if [ -z "$FOCUS" ]; then
    echo "Focus failed:"; echo "$FOCUS_OUT"; exit 1
fi
echo "focus: $FOCUS"
sleep 0.5

# 4. Optional game mode for mimic tests.
[ "$MIMIC" = 1 ] && repl "actions.user.claude_enter_game_mode()" | json_of | sed 's/^/modes: /'

# 5. Run the test command.
echo "----- REPL: $CMD -----"
CMD_OUT="$(repl "$CMD")"
echo "$CMD_OUT"
echo "----- end REPL -----"
CMD_FAILED=0
echo "$CMD_OUT" | grep -q '^Traceback' && CMD_FAILED=1

# 6. Let cron-driven effects play out while the game is focused.
sleep "$WAIT"

# 7. Optional screenshot while the game is still frontmost.
if [ "$SCREENSHOT" = 1 ]; then
    repl "actions.user.capture_claude_screenshot()" | grep -i 'screenshot'
fi
[ "$CMD_FAILED" = 1 ] && { echo "REPL COMMAND RAISED AN EXCEPTION"; exit 1; }
exit 0
