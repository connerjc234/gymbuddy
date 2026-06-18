# Draft: GymBuddy Codebase Cleanup & Main Window Redesign

## Status: Awaiting Approval

## Analysis Complete

### Current State (pure LOC)
| File | LOC | Verdict |
|------|-----|---------|
| `ui/main_window.py` | 764 | **DEFECT** - over 250, single orchestrator doing everything |
| `ui/theme.py` | 527 | **DEFECT** - over 250, constant+stylesheet soup |
| `ui/workout_dialog.py` | 476 | **DEFECT** - over 250 |
| `core/storage.py` | 440 | **DEFECT** - over 250, god class |
| `ui/ai_chat_dialog.py` | 289 | **DEFECT** - over 250, possibly dead code |
| `ui/supplement_dialog.py` | 223 | Warning band |
| `core/openai_client.py` | 206 | Warning band |
| `ui/calendar_widget.py` | 199 | Healthy |
| `core/models.py` | 179 | Healthy |
| `ui/template_dialog.py` | 139 | Healthy |
| `ui/goal_dialog.py` | 132 | Healthy |
| `core/ai_client.py` | 129 | Healthy |
| `ui/progress_chart.py` | 122 | Healthy |
| `core/calculator.py` | 70 | Healthy |
| `ui/exercise_dialog.py` | 70 | Healthy |
| `core/config.py` | 67 | Healthy |
| `main.py` | 35 | Healthy |

### Architecture Issues Identified
1. **No tests** — zero test files exist
2. **`VaultStorage` god class** — single class handles workouts, goals, templates, supplements, exercise library, monthly progress, AI notes
3. **`MainWindow` monolith** — does layout, data loading, stats, workouts display, goals, AI chat, templates, supplements, settings, keyboard shortcuts
4. **`theme.py`** — color constants mixed with 400+ line stylesheet string
5. **AI code possibly dead** — `ai_enabled: false` by default, `ai_chat_dialog.py` unused unless enabled

### Key Decisions Made
- **Split strategy**: Storage split by entity (not by concern) — each entity type gets its own store file
- **Main window split**: Extract sidebar, workout panel, goals panel, stats into separate widget files
- **Theme split**: Constants in `theme/colors.py`, stylesheet in `theme/styles.py` or separate CSS-like files
- **Dead code**: Keep `ai_client.py` (ABC + MockAIClient) but remove `openai_client.py` and `ai_chat_dialog.py` if not actively used — ASK USER
- **Tests**: pytest with characterization tests BEFORE any refactoring to pin behavior
- **Approach**: Waves — (0) tests, (1) models/config, (2) storage, (3) theme, (4) UI panels, (5) main window redesign, (6) verification

### Pending User Decisions
1. Remove `openai_client.py` + `ai_chat_dialog.py` dead AI code? (ai_enabled=false by default, these are 495 combined LOC)
2. Prefer flat `storage/` module or entity-prefixed files like `workout_store.py`?
3. Main window redesign scope: just extract sections OR also improve layout/visuals?
