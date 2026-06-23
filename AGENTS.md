# Repository Guidelines

## Project Structure & Module Organization

This repository is a personal Talon voice-control package. Root-level `.talon` and `.py` files provide general commands and integrations. Gaming automation lives under `gaming/`: put shared actions in `gaming/helpers/`, per-game voice mappings in `gaming/games/`, OCR cursor templates in `gaming/cursors/<game_name>/`, and clickable image templates in `gaming/images_to_click/`. Custom spoken vocabularies belong in `controlled_vocabularies/`; language-specific extensions belong in `languages/`. `claude_helpers/` contains development utilities and captured screenshots. Sibling packages under `~/.talon/user/` are external dependencies and must not be modified as part of this repository.

## Build, Test, and Development Commands

There is no separate build step: Talon automatically reloads `.talon` files and usually hot-reloads Python modules.

```bash
tail -20 /Users/jarrod/.talon/talon.log
echo 'app.notify("test")' | /Users/jarrod/.talon/bin/repl
python -m py_compile path/to/changed_file.py
```

Check the Talon log after every edit for parse, import, and runtime errors. Use the REPL to exercise actions in Talon's actual environment. If a Python dependency is required, install it with `/Users/jarrod/.talon/bin/pip`, not the system `pip`.

## Coding Style & Naming Conventions

Use four-space indentation and `snake_case` for Python functions, actions, settings, and filenames. Keep action declarations in a documented `@mod.action_class`; retain global references for cron jobs so they can be cancelled before replacement. Name game files and asset directories consistently, for example `gaming/games/chained_echoes.talon` and `gaming/cursors/chained_echoes/`. In Talonscript, keep comments on their own lines and split complex arithmetic into one operation per line.

## Testing Guidelines

The repository has no automated test suite or coverage threshold. Validate changed Python syntax, trigger affected actions through the Talon REPL or voice command, and inspect the log again. Game and OCR changes require an in-game check with representative menus and templates. Do not introduce grid-based menu navigation; use direct coordinates and proximity thresholds.

## Commit & Pull Request Guidelines

Recent commits use short, imperative subjects such as `Add 3D movement...`, `Fix multi-word phrase matching...`, and `Remove paper_perjury game config`. Keep each commit focused. Pull requests should explain the user-visible behavior, list manual validation performed, link any issue, and include screenshots when OCR regions, cursor templates, or overlays change. Never commit generated `__pycache__` files.
