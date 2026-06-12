# Workout Tracker

A PyQt6 desktop app for logging workouts and tracking progress, with direct Obsidian vault integration.

## Features

- **Daily workout logging** — exercises, sets, reps, weight, RPE
- **Goal tracking** — set targets with dates (e.g., "Bench 225×5 by Aug 15, 2026")
- **Obsidian integration** — writes markdown files directly to your vault
- **Progress visualization** — volume charts, goal progress bars
- **Dark theme** — consistent with VinylRipper

## Quick Start

```bash
./setup.sh
source .venv/bin/activate
python -m workout_tracker.main
```

## Project Structure

```
workout_tracker/
├── main.py                 # Entry point
├── core/
│   ├── config.py           # Configuration management
│   ├── models.py           # Data models (Workout, Exercise, Set, Goal)
│   ├── storage.py          # Obsidian vault read/write
│   ├── calculator.py       # Volume, 1RM, progression math
│   └── ai_client.py        # AI integration interface (future)
└── ui/
    ├── main_window.py      # Main application window
    ├── workout_dialog.py   # Log/edit workout
    ├── goal_dialog.py      # Set/edit goals
    ├── calendar_widget.py  # Custom calendar with workout indicators
    ├── progress_chart.py   # Progress charts
    └── theme.py            # Dark theme stylesheet
```

## Configuration

Config stored at `~/.config/workout-tracker/config.json`:

```json
{
  "vault_path": "/home/conner/Documents/ObsidianVault",
  "units": "metric",
  "default_split": "PPL",
  "theme": "dark",
  "ai_enabled": false,
  "ai_provider": "openai"
}
```

## Obsidian Vault Structure

The app reads/writes to these paths in your vault:

```
Gym/
├── Workouts/
│   └── 2026-06-11.md       # Daily workout logs
├── Goals/
│   └── 2026-08-15-bench-225.md  # Goal tracking
├── Progress-2026-06.md     # Monthly summaries (appended)
└── Overview.md             # Split/exercise library (synced)
```

## Development

```bash
# Format & lint
ruff check --fix .
ruff format .

# Type check
mypy workout_tracker

# Run tests
pytest
```