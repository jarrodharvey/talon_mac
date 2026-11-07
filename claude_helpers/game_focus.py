"""
Focus-aware game testing helpers for Claude Code.

Claude Code runs in the terminal, so game-specific REPL tests normally execute
while the terminal (not the game) is frontmost. These actions let
claude_helpers/game_test.sh bring the game window matching a game's .talon
context header into focus, run a test, and then restore the terminal.

Every action prints a single-line JSON result prefixed with CLAUDE_GAME_JSON:
so the shell wrapper can parse it out of the REPL output.
"""

import json
import re
import subprocess
import time

from talon import Module, actions, scope, storage, ui

mod = Module()

STREAMING_APPS = ("moonlight", "nvidia geforce now")

TOGGLED_MODES = ("sleep", "command", "dictation", "user.game")
TERMINAL_APPS = ("Terminal", "iTerm2", "Code", "Ghostty", "WezTerm", "kitty")

_saved_window = None
_saved_modes = None


def _emit(payload: dict):
    print("CLAUDE_GAME_JSON:" + json.dumps(payload))


def _parse_header(talon_path: str) -> dict:
    """Parse the context header (everything before the '-' line) of a .talon file."""
    apps, titles, modes, manual_games = [], [], [], []
    with open(talon_path) as f:
        lines = f.read().splitlines()
    if "-" not in [l.strip() for l in lines]:
        raise ValueError(f"{talon_path} has no context header ('-' separator)")
    for raw in lines:
        line = raw.strip()
        if line == "-":
            break
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key, value = key.strip().lower(), value.strip()
        if key.startswith("and "):
            key = key[4:].strip()
        if key in ("app", "app.name"):
            apps.append(value)
        elif key in ("title", "win.title"):
            titles.append(value)
        elif key == "mode":
            modes.append(value)
        elif key == "user.active_manual_game":
            manual_games.append(value)
    if not apps:
        raise ValueError(f"{talon_path} header has no app: line")
    return {"apps": apps, "titles": titles, "modes": modes, "manual_games": manual_games}


def _manual_game_check(header: dict, app) -> dict:
    """Streaming apps host many games; user.active_manual_game says which one is live."""
    if app is None or app.name.lower() not in STREAMING_APPS:
        return {"applies": False, "matches": True}
    current = storage.get("user.manual_game")
    if not header["manual_games"]:
        return {"applies": False, "matches": True, "active_manual_game": current}
    matches = (current or "").strip().lower() in {g.lower() for g in header["manual_games"]}
    return {"applies": True, "matches": matches, "active_manual_game": current,
            "expected": header["manual_games"]}


def _title_matcher(spec: str):
    m = re.fullmatch(r"/(.*)/([a-z]*)", spec)
    if m:
        flags = re.IGNORECASE if "i" in m.group(2) else 0
        rx = re.compile(m.group(1), flags)
        return lambda t: bool(rx.search(t))
    return lambda t: t == spec


def _find_game_window(header: dict):
    """Return (app, window) for the first window matching the header, else (None, None)."""
    wanted = {a.lower() for a in header["apps"]}
    matchers = [_title_matcher(t) for t in header["titles"]]
    for app in ui.apps(background=False):
        if app.name.lower() not in wanted:
            continue
        # Skip tiny helper windows (e.g. Moonlight's 37px menu-bar strip); prefer the largest.
        candidates = [w for w in app.windows() if w.rect.height >= 100 and w.rect.width >= 100]
        if matchers:
            candidates = [w for w in candidates if any(m(w.title) for m in matchers)]
        if candidates:
            return app, max(candidates, key=lambda w: w.rect.width * w.rect.height)
    return None, None


def _wait_for(predicate, error: str, timeout: float = 3.0):
    t0 = time.perf_counter()
    while not predicate():
        if time.perf_counter() - t0 > timeout:
            raise RuntimeError(error)
        actions.sleep(0.1)


def _current_modes():
    return sorted(scope.get("mode") or [])


@mod.action_class
class Actions:
    def claude_game_status(talon_path: str):
        """Report whether the game matching a .talon file's context header is running"""
        header = _parse_header(talon_path)
        app, window = _find_game_window(header)
        manual = _manual_game_check(header, app)
        _emit({
            "running": window is not None,
            "game_matches": window is not None and manual["matches"],
            "manual_game": manual,
            "app": app.name if app else None,
            "window_title": window.title if window else None,
            "header": header,
            "frontmost_app": ui.active_app().name,
            "modes": _current_modes(),
        })

    def claude_focus_game(talon_path: str):
        """Save the current window, then focus the game window matching a .talon file's header"""
        global _saved_window
        header = _parse_header(talon_path)
        app, window = _find_game_window(header)
        if window is None:
            raise RuntimeError(f"No running window matches header {header}")
        manual = _manual_game_check(header, app)
        if not manual["matches"]:
            raise RuntimeError(f"{app.name} is streaming {manual['active_manual_game']!r}, "
                               f"not {manual['expected']}")
        _saved_window = ui.active_window()
        # Talon's app.focus()/window.focus() can't reliably raise Moonlight's fullscreen
        # window (it reports hidden=True); AppleScript `activate` does.
        subprocess.run(
            ["osascript", "-e", f'tell application id "{app.bundle}" to activate'],
            check=True, capture_output=True, timeout=5,
        )
        _wait_for(lambda: ui.active_app() == app, f"Can't focus app: {app.name}", timeout=5.0)
        if ui.active_window() != window:
            window.focus()
            _wait_for(lambda: ui.active_window() == window, f"Can't focus window: {window.title!r}")
        _emit({
            "focused": True,
            "app": app.name,
            "window_title": window.title,
            "saved_app": _saved_window.app.name if _saved_window else None,
        })

    def claude_restore_focus():
        """Refocus the window saved by claude_focus_game (falls back to a terminal app)"""
        global _saved_window
        target = _saved_window
        _saved_window = None
        if target is not None:
            try:
                actions.user.switcher_focus_window(target)
                _emit({"restored": True, "app": target.app.name})
                return
            except Exception as e:
                print(f"claude_restore_focus: saved window unavailable ({e}), trying terminal apps")
        for app in ui.apps(background=False):
            if app.name in TERMINAL_APPS:
                actions.user.switcher_focus_app(app)
                _emit({"restored": True, "app": app.name, "fallback": True})
                return
        raise RuntimeError("claude_restore_focus: no saved window and no terminal app running")

    def claude_enter_game_mode():
        """Save current modes, then switch to game mode (for mimic-based tests)"""
        global _saved_modes
        _saved_modes = [m for m in _current_modes() if m in TOGGLED_MODES]
        actions.user.game_mode()
        _emit({"saved_modes": _saved_modes, "modes": _current_modes()})

    def claude_restore_modes():
        """Restore the modes saved by claude_enter_game_mode"""
        global _saved_modes
        if _saved_modes is None:
            raise RuntimeError("claude_restore_modes: no saved modes")
        for m in TOGGLED_MODES:
            if m in _saved_modes:
                actions.mode.enable(m)
            else:
                actions.mode.disable(m)
        restored = _saved_modes
        _saved_modes = None
        _emit({"restored_modes": restored, "modes": _current_modes()})
