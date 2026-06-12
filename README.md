# GymBuddy

A premium PyQt6 workout tracker with Obsidian vault integration — warm editorial design, distinctive typography, and meticulous attention to detail.

## Aesthetic

- **Palette**: Warm parchment (#f5f2ec), terracotta accent (#d64550), pure white cards
- **Typography**: Oswald (display headers), Source Sans 3 (body), Playfair Display (accent)
- **Vibe**: Warm premium editorial — think Nike Training Club meets a refined print magazine

## Features

- **Daily workout logging** — exercises, sets, reps, weight, RPE
- **Goal tracking** — set targets with dates (summer goal: Aug 15, 2026)
- **Split presets** — Push/Pull/Legs/Upper/Lower/Full Body auto-populate exercises
- **Exercise library** — manage from GymBuddy, syncs to `Gym/Overview.md`
- **Obsidian integration** — writes markdown to your vault in real-time
- **Progress visualization** — volume chart with goal lines, consistency streak, stat cards
- **Keyboard shortcuts** — Ctrl+N (log), Ctrl+D (delete), Ctrl+T (today), Ctrl+G (goal)

## Quick Start

```bash
./setup.sh
source .venv/bin/activate
python -m workout_tracker.main
```

## Project Structure

```
workout_tracker/
├── main.py                 # Entry point (GymBuddy)
├── core/
│   ├── config.py           # Vault path, units, theme
│   ├── models.py           # Dataclasses
│   ├── storage.py          # Obsidian vault read/write
│   ├── calculator.py       # 1RM, volume, progression
│   └── ai_client.py        # AI interface (future)
└── ui/
    ├── main_window.py      # Main window
    ├── workout_dialog.py   # Log/edit workout
    ├── goal_dialog.py      # Set/edit goals
    ├── exercise_dialog.py  # Manage exercise library
    ├── calendar_widget.py  # Custom monthly calendar
    ├── progress_chart.py   # Volume-over-time chart
    └── theme.py            # Warm premium theme
```

## Configuration

`~/.config/workout-tracker/config.json`:
```json
{
  "vault_path": "/home/conner/Documents/ObsidianVault",
  "units": "metric",
  "default_split": "PPL",
  "theme": "warm",
  "ai_enabled": false
}
```

## Vault Integration

```
Gym/
├── Workouts/YYYY-MM-DD.md       # Daily logs
├── Goals/YYYY-MM-DD-name.md     # Goal tracking
├── Progress-YYYY-MM.md          # Monthly summaries
└── Overview.md                  # Exercise library
```

## Development

```bash
ruff check --fix . && ruff format .
mypy workout_tracker
pytest
```