# GymBuddy Codebase Cleanup & Main Window Redesign

## TL;DR (For humans)

The codebase has 5 files over the 250-LOC ceiling, zero tests, a god-class storage layer, and a monolithic main window. This plan splits oversized files by responsibility, adds characterization tests first, then refactors in waves: storage → theme → workout dialog → main window panels → verification.

**Estimated: 6-8 waves, each independently verifiable. No functional changes — pure structural cleanup.**

---

## Current State (pure LOC)

| File | LOC | Verdict | Action |
|------|-----|---------|--------|
| `ui/main_window.py` | 764 | OVER | Split into panels |
| `ui/theme.py` | 527 | OVER (data table exception) | Split constants from stylesheet |
| `ui/workout_dialog.py` | 476 | OVER | Split ExerciseRow + ExerciseListWidget |
| `core/storage.py` | 440 | OVER | Split by entity |
| `ui/ai_chat_dialog.py` | 289 | OVER (dead?) | Keep (see decision #1) |
| `ui/supplement_dialog.py` | 223 | Warning | Monitor |
| `core/openai_client.py` | 206 | Warning | Keep (feature-flagged) |
| All others | ≤199 | Healthy | No changes needed |

---

## Implementation Plan

### Wave 0 — Test Infrastructure & Characterization Tests

**Goal**: Pin current behavior before any structural changes.

**Files to create:**
- `tests/__init__.py` — empty
- `tests/conftest.py` — pytest fixtures (sample workout, sample goal, temp vault dir)
- `tests/test_models.py` — Set, Exercise, Workout, Goal property tests
- `tests/test_calculator.py` — epley_1rm, consistency_streak, suggest_progression
- `tests/test_storage.py` — VaultStorage CRUD against temp directory

**Key test scenarios:**
- `test_set_volume`: Set(weight=100, reps=5).volume == 500
- `test_estimated_1rm`: Set(weight=100, reps=5).estimated_1rm == 116.67 (approx)
- `test_workout_total_volume`: sums exercise volumes
- `test_goal_properties`: is_complete, days_remaining, progress_pct
- `test_consistency_streak`: [mon, tue, wed] -> 3; [mon, wed, fri] -> 1
- `test_storage_save_load_workout`: save then load, assert all fields match
- `test_storage_save_load_goal`: save then load, assert all fields match
- `test_storage_exercise_library`: save then load, assert roundtrip

**Files to modify:**
- `pyproject.toml` — uncomment/add pytest config, ensure `tests/` not excluded

**Acceptance**: `pytest tests/ -v` passes with ≥15 tests.
**Commit message**: `chore: add test infrastructure and characterization tests`

---

### Wave 1 — Core Cleanup (models, config, calculator)

**Goal**: Minor tightening of the already-healthy files.

**Changes to `core/models.py`:**
- No structural changes (179 LOC, healthy, widely depended on)
- Add `__slots__` to dataclasses (Set, Exercise, Workout, Goal, Supplement) for perf — wait, dataclasses with `slots=True` require Python 3.10+ (we have 3.11) but will break pickle/serialization if any code relies on it. SKIP for this cleanup.
- Add `__str__` methods for debugging? Optional, low priority.

**Changes to `core/config.py`:**
- No changes needed (67 LOC, clean, well-typed)

**Changes to `core/calculator.py`:**
- No changes needed (70 LOC, clean, well-typed)

**Acceptance**: Existing tests still pass, mypy clean.
**Commit message**: `chore: core models cleanup (minor typing improvements)`

---

### Wave 2 — Storage Refactor

**Goal**: Split `VaultStorage` god class (440 LOC) into entity-specific stores (<250 LOC each).

**New file structure:**
```
workout_tracker/core/storage/
├── __init__.py          # Barrel: re-exports, backward-compat VaultStorage facade
├── base.py              # BaseStore with shared helpers (_parse_frontmatter, _write_frontmatter)
├── workout_store.py     # Workout CRUD + list + delete (<250 LOC)
├── goal_store.py        # Goal CRUD + delete (<120 LOC)
├── template_store.py    # Template CRUD + list + delete (<150 LOC)
├── supplement_store.py  # Supplement CRUD + delete (<100 LOC)
├── exercise_store.py    # Exercise library read/write (<100 LOC)
├── progress_store.py    # Monthly progress append (<60 LOC)
└── ai_store.py          # AI notes save (<50 LOC)
```

**Design decisions:**
- `BaseStore` takes `config` in constructor, provides `_parse_frontmatter()`, `_write_frontmatter()`
- Each store class takes `config` (or parent store), exposes only its entity's methods
- `VaultStorage` facade in `__init__.py` delegates to all stores, keeps same public API
- No import changes needed in callers (they all use `VaultStorage`)

**Acceptance**: All existing tests pass (characterization tests from Wave 0 still pass against facade). Each new file ≤200 LOC.
**Commit message**: `refactor(core): split VaultStorage into entity-specific stores`

---

### Wave 3 — Theme Cleanup

**Goal**: Split theme.py into logical modules. The 527 LOC is mostly a stylesheet string (data table — acceptable size exception), but mixing constants with a huge f-string is messy.

**New file structure:**
```
workout_tracker/ui/theme/
├── __init__.py    # Barrel: re-exports get_stylesheet(), register_fonts(), FONT_*, color constants
├── colors.py      # Color constants (BG_WARM, ACCENT_TERRACOTTA, etc.) — ~30 LOC
├── fonts.py       # Font names + register_fonts() — ~55 LOC
└── styles.py      # STYLESHEET + CARD_STYLE + STAT_CARD + get_stylesheet() — ~510 LOC
```

**Backward compatibility:**
- `from .theme import FONT_DISPLAY` still works (re-exported from `__init__.py`)
- `from .theme import get_stylesheet` still works
- `from .theme import register_fonts` still works
- All 9 imports across the codebase remain unchanged

**Acceptance**: App launches with correct theming. All `from .theme import X` imports resolve.
**Commit message**: `refactor(ui): split theme into colors/fonts/styles modules`

---

### Wave 4 — Workout Dialog Split

**Goal**: workout_dialog.py (476 LOC) has 3 classes — WorkoutDialog, ExerciseRow, ExerciseListWidget. Extract ExerciseRow and ExerciseListWidget into their own files.

**New file structure:**
```
workout_tracker/ui/
├── workout_dialog.py        # WorkoutDialog only (~200 LOC after extraction)
├── exercise_row.py          # ExerciseRow widget (~200 LOC) 
└── exercise_list_widget.py  # ExerciseListWidget (~50 LOC)
```

**No backward compat needed** — ExerciseRow and ExerciseListWidget are only imported/used by WorkoutDialog.

**Acceptance**: Workout dialog opens, exercises can be added/edited/removed, save works.
**Commit message**: `refactor(ui): split workout_dialog into separate widget files`

---

### Wave 5 — Main Window Panel Extraction

**Goal**: Extract sections from MainWindow (764 LOC) into separate widget files. MainWindow becomes a thin orchestrator (~250 LOC).

**Extraction targets:**
1. **Sidebar** (calendar + stat cards + action buttons) → `ui/panels/sidebar_panel.py`
2. **Workout display** (workout card + edit/delete/save-as-template + exercise list) → `ui/panels/workout_panel.py`
3. **Goals display** (goals scroll area) → `ui/panels/goals_panel.py`

**New file structure:**
```
workout_tracker/ui/panels/
├── __init__.py          # Barrel
├── sidebar_panel.py     # CalendarWidget + StatCard rows + action buttons (~180 LOC)
├── workout_panel.py     # WorkoutSummaryCard + workout display/exercise list (~220 LOC)
└── goals_panel.py       # GoalCard list (~120 LOC)
```

**Panel interface (each panel emits signals, MainWindow connects):**
```python
class SidebarPanel(QWidget):
    def set_workout_dates(self, dates: list[date]) -> None: ...
    def set_goal_dates(self, dates: list[date]) -> None: ...
    def set_stats(self, streak: int, total: int, volume: float) -> None: ...
    # signals
    date_selected = pyqtSignal(date)
    new_workout_requested = pyqtSignal()
    new_goal_requested = pyqtSignal()
    settings_requested = pyqtSignal()

class WorkoutPanel(QWidget):
    def show_workout(self, selected_date: date, workout: Workout | None) -> None: ...
    # signals
    edit_requested = pyqtSignal(date)
    delete_requested = pyqtSignal(date)
    save_as_template_requested = pyqtSignal(Workout)

class GoalsPanel(QWidget):
    def set_goals(self, goals: list[Goal]) -> None: ...
    # signals
    edit_requested = pyqtSignal(Goal)
    delete_requested = pyqtSignal(Goal)
```

**MainWindow changes:**
- Instantiate 3 panels in `_setup_ui()` instead of building widgets inline
- Connect panel signals to existing handlers
- `_load_data()` calls panel methods instead of direct widget manipulation
- Menu bar and keyboard shortcuts stay in MainWindow
- D-Bus and notification init stay in MainWindow

**Acceptance**: App launches, all panels render correctly, navigation/CRUD works via panels.
**Commit message**: `refactor(ui): extract sidebar, workout, goals panels from MainWindow`

---

### Wave 6 — Dead Code Assessment

**Goal**: Address `openai_client.py` and `ai_chat_dialog.py`.

**Decision**: KEEP both since:
- `ai_enabled` is a config option someone may use
- The abstraction layer (`ai_client.py` ABC + MockAIClient) is clean
- Removing would be a breaking change for anyone who configured AI

**Changes**: None. Flag in documentation only.

---

### Wave 7 — Verification

**Goal**: Full verification pipeline.

**Steps:**
1. `ruff check --fix . && ruff format .` — zero warnings
2. `mypy workout_tracker` — zero errors
3. `pytest tests/ -v` — all tests pass
4. `python -m workout_tracker.main` — launches without import errors (verify with timeout)
5. Manual smoke test of key workflows:
   - Calendar navigation
   - Log workout dialog opens and saves
   - Goal dialog opens and saves  
   - Supplement dialog
   - Stats/streak display
   - Chart renders

**Acceptance**: All 5 verification steps pass.
**Commit message**: `chore: final cleanup and verification`

---

## Import Map (Critical — Must Update References)

When files are moved/split, update ALL imports. Here's every import that references moved modules:

### Storage imports (Wave 2)
| File | Current import | New import |
|------|---------------|------------|
| `main_window.py` | `from ..core.storage import VaultStorage` | Same (facade) |
| `template_dialog.py` | `from ..core.storage import VaultStorage` | Same (facade) |
| `ai_chat_dialog.py` | `from ..core.storage import VaultStorage` | Same (facade) |

### Theme imports (Wave 3)
All `from .theme import X` — unchanged (barrel re-exports from `__init__.py`).

| File | Imports theme symbols |
|------|----------------------|
| `main_window.py` | `FONT_DISPLAY`, `get_stylesheet`, `BG_WARM`, etc. |
| `workout_dialog.py` | `FONT_BODY`, `FONT_DISPLAY` |
| `calendar_widget.py` | `FONT_BODY`, `FONT_DISPLAY`, colors |
| `progress_chart.py` | `FONT_BODY`, `FONT_DISPLAY` |
| `ai_chat_dialog.py` | Multiple color/font constants |
| `exercise_dialog.py` | `FONT_DISPLAY` |
| `goal_dialog.py` | `FONT_DISPLAY` |
| `supplement_dialog.py` | (none — inline styles) |

### Workout dialog imports (Wave 4)
`exercise_row.py` and `exercise_list_widget.py` are only used by `workout_dialog.py` — local import change only.

### Main window imports (Wave 5)
No external import changes — panels stay within `ui/` package.

---

## Dependency Matrix

```
Wave 0 (tests) ──► Wave 1 (core)
Wave 0 (tests) ──► Wave 2 (storage) ──► Wave 5 (main window panels)
Wave 0 (tests) ──► Wave 3 (theme)    ──► Wave 5
Wave 0 (tests) ──► Wave 4 (workout dialog)
Wave 5 (panels)  ──► Wave 7 (verification)
Waves 1-4        ──► Wave 7 (verification)
```

Waves 1-4 are independent and can be done in parallel. Wave 5 depends on Wave 2 (storage) and Wave 3 (theme). Wave 7 depends on all prior waves.

---

## Verification Strategy

### For each wave:
1. **Pre-condition**: Run `ruff check . && ruff format . && mypy workout_tracker` — green
2. **During**: Edit/create files
3. **Post-condition**: Run `ruff check . && ruff format . && mypy workout_tracker` — green
4. **Run tests**: `pytest tests/ -v` — green
5. **Run app**: `timeout 3 python -m workout_tracker.main || true` — no import/traceback errors

### Post-verification gate (Wave 7):
- All ruff/mypy/pytest green
- App launches (import check)
- Manual smoke test logged
