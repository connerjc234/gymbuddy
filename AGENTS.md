# Workout Tracker — Agent Instructions

## Project Context

- **Type**: Python GUI (PyQt6) desktop app
- **Obsidian Integration**: Direct markdown file writes to vault
- **Goal Date**: August 15, 2026
- **Stack**: Python 3.11+, PyQt6, ruff (line-length 88), mypy strict

## Conventions

- Follow VinylRipper architecture patterns (core/ui separation, config system, dark theme)
- Type hints required everywhere; mypy strict enabled
- Format with ruff (line-length 88)
- Dataclasses for models, ABC for interfaces
- Qt signals/slots for UI-core communication

## Key Files

| File | Purpose |
|------|---------|
| `workout_tracker/main.py` | Entry point |
| `workout_tracker/core/config.py` | Vault path, units, theme |
| `workout_tracker/core/models.py` | Workout, Exercise, Set, Goal dataclasses |
| `workout_tracker/core/storage.py` | Obsidian markdown read/write |
| `workout_tracker/ui/main_window.py` | Main window with calendar + workout list |
| `workout_tracker/ui/theme.py` | Shared dark theme stylesheet |

## Commands

```bash
# Format & lint
ruff check --fix .
ruff format .

# Type check
mypy workout_tracker

# Run app
python -m workout_tracker.main
```

## Obsidian Vault Path

`/home/conner/Documents/ObsidianVault/Gym/`

## Session Logging

After meaningful work, append to `Projects/WorkoutTracker/Session-YYYY-MM-DD.md` in the vault.