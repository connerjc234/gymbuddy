"""Characterization tests for VaultStorage.

Pins current behavior of vault read/write operations before any refactoring.
Uses a temp directory as the vault to avoid touching the real Obsidian vault.
"""

from datetime import date
from pathlib import Path

import pytest

from workout_tracker.core.config import Config
from workout_tracker.core.models import (
    Exercise,
    Goal,
    GoalMetric,
    Set,
    Supplement,
    SupplementFrequency,
    SupplementTiming,
    Workout,
    WorkoutTemplate,
)
from workout_tracker.core.storage import VaultStorage


@pytest.fixture
def config_with_temp_vault(tmp_path: Path) -> Config:
    """Create a Config pointing at a temporary vault path."""
    vault = tmp_path / "ObsidianVault"
    cfg = Config(vault_path=str(vault))
    cfg.ensure_dirs()
    return cfg


@pytest.fixture
def storage(config_with_temp_vault: Config) -> VaultStorage:
    """Create a VaultStorage backed by temp directory."""
    # Patch the config by instantiating with the temp config
    # VaultStorage reads from get_config(), so we need to set it
    import workout_tracker.core.config as cfg_module

    # Save original
    orig = cfg_module._config
    cfg_module._config = config_with_temp_vault

    store = VaultStorage()
    yield store

    # Restore
    cfg_module._config = orig


# ── Workout Storage ──


class TestWorkoutStorage:
    def test_save_and_load_workout(self, storage: VaultStorage) -> None:
        w = Workout(
            date=date(2026, 6, 1),
            exercises=[
                Exercise(
                    name="Bench Press",
                    order=0,
                    sets=[
                        Set(weight=100, reps=5, rpe=8.0, set_number=1),
                        Set(weight=90, reps=8, rpe=7.5, set_number=2),
                    ],
                    notes="Felt strong",
                ),
                Exercise(
                    name="Squat",
                    order=1,
                    sets=[Set(weight=140, reps=5, set_number=1)],
                ),
            ],
            split_day="Push",
            duration_min=45,
            notes="Great session",
        )
        storage.save_workout(w)
        loaded = storage.load_workout(date(2026, 6, 1))
        assert loaded is not None
        assert loaded.date == w.date
        assert loaded.split_day == w.split_day
        assert loaded.duration_min == w.duration_min
        assert loaded.notes == w.notes
        assert loaded.completed == w.completed
        assert len(loaded.exercises) == 2
        assert loaded.exercises[0].name == "Bench Press"
        assert loaded.exercises[0].sets[0].weight == 100
        assert loaded.exercises[0].sets[1].reps == 8
        # Note: Exercise notes are written to markdown but NOT parsed back on load
        assert loaded.exercises[0].notes == ""

    def test_load_nonexistent_workout(self, storage: VaultStorage) -> None:
        loaded = storage.load_workout(date(2025, 1, 1))
        assert loaded is None

    def test_list_workout_dates(self, storage: VaultStorage) -> None:
        dates = [date(2026, 6, 1), date(2026, 6, 3), date(2026, 6, 5)]
        for d in dates:
            storage.save_workout(Workout(date=d))
        listed = storage.list_workout_dates()
        assert listed == dates  # Should be sorted

    def test_delete_workout(self, storage: VaultStorage) -> None:
        d = date(2026, 6, 1)
        storage.save_workout(Workout(date=d))
        storage.delete_workout(d)
        assert storage.load_workout(d) is None
        assert d not in storage.list_workout_dates()

    def test_save_workout_overwrites(self, storage: VaultStorage) -> None:
        d = date(2026, 6, 1)
        storage.save_workout(Workout(date=d, notes="First"))
        storage.save_workout(Workout(date=d, notes="Second"))
        loaded = storage.load_workout(d)
        assert loaded is not None
        assert loaded.notes == "Second"


# ── Goal Storage ──


class TestGoalStorage:
    def test_save_and_load_goal(self, storage: VaultStorage) -> None:
        g = Goal(
            name="Bench 225",
            target_date=date(2026, 8, 15),
            metric=GoalMetric.WEIGHT,
            target_value=225.0,
            current_value=185.0,
            exercise_name="Bench Press",
            notes="Progressing well",
        )
        storage.save_goal(g)
        goals = storage.load_goals()
        assert len(goals) >= 1
        loaded = goals[-1]
        assert loaded.name == g.name
        assert loaded.target_date == g.target_date
        assert loaded.metric == g.metric
        assert loaded.target_value == g.target_value
        assert loaded.current_value == g.current_value
        assert loaded.exercise_name == g.exercise_name
        # Note: Goal notes contain the full markdown body (auto-generated display + user notes)
        assert g.notes in loaded.notes  # User notes are contained within

    def test_delete_goal(self, storage: VaultStorage) -> None:
        g = Goal(
            name="Test Goal",
            target_date=date(2026, 8, 15),
            metric=GoalMetric.WEIGHT,
            target_value=100,
        )
        storage.save_goal(g)
        assert len(storage.load_goals()) >= 1
        storage.delete_goal(g)
        names = [goal.name for goal in storage.load_goals()]
        assert "Test Goal" not in names

    def test_goals_sorted_by_date(self, storage: VaultStorage) -> None:
        g1 = Goal(
            name="Goal B",
            target_date=date(2026, 9, 1),
            metric=GoalMetric.WEIGHT,
            target_value=100,
        )
        g2 = Goal(
            name="Goal A",
            target_date=date(2026, 8, 1),
            metric=GoalMetric.WEIGHT,
            target_value=100,
        )
        storage.save_goal(g1)
        storage.save_goal(g2)
        goals = storage.load_goals()
        dates = [g.target_date for g in goals[-2:]]
        assert dates == sorted(dates)


# ── Exercise Library ──


class TestExerciseLibrary:
    def test_save_and_load_exercises(self, storage: VaultStorage) -> None:
        exercises = ["Bench Press", "Squat", "Deadlift"]
        storage.save_exercise_library(exercises)
        loaded = storage.load_exercise_library()
        for ex in exercises:
            assert ex in loaded

    def test_empty_library(self, storage: VaultStorage) -> None:
        assert storage.load_exercise_library() == []


# ── Template Storage ──


class TestTemplateStorage:
    def test_save_and_load_template(self, storage: VaultStorage) -> None:
        t = WorkoutTemplate(
            name="Push Day",
            exercises=[
                Exercise(
                    name="Bench Press",
                    order=0,
                    sets=[Set(weight=0, reps=8, rpe=7.0, set_number=1)],
                ),
            ],
            split_day="Push",
            notes="Standard push",
        )
        storage.save_template(t)
        loaded = storage.load_template("Push Day")
        assert loaded is not None
        assert loaded.name == "Push Day"
        assert loaded.split_day == "Push"
        assert len(loaded.exercises) == 1
        assert loaded.notes == "Standard push"

    def test_list_templates(self, storage: VaultStorage) -> None:
        storage.save_template(WorkoutTemplate(name="A"))
        storage.save_template(WorkoutTemplate(name="B"))
        names = storage.list_templates()
        assert "A" in names
        assert "B" in names

    def test_delete_template(self, storage: VaultStorage) -> None:
        storage.save_template(WorkoutTemplate(name="Delete Me"))
        assert "Delete Me" in storage.list_templates()
        storage.delete_template("Delete Me")
        assert "Delete Me" not in storage.list_templates()

    def test_load_nonexistent_template(self, storage: VaultStorage) -> None:
        assert storage.load_template("NONEXISTENT") is None


# ── Supplement Storage ──


class TestSupplementStorage:
    def test_save_and_load_supplement(self, storage: VaultStorage) -> None:
        s = Supplement(
            name="Creatine",
            dosage="5g",
            frequency=SupplementFrequency.DAILY,
            timing=SupplementTiming.PRE_WORKOUT,
            notes="Load phase done",
        )
        storage.save_supplement(s)
        supplements = storage.load_supplements()
        assert len(supplements) >= 1
        loaded = supplements[-1]
        assert loaded.name == "Creatine"
        assert loaded.dosage == "5g"
        assert loaded.frequency == SupplementFrequency.DAILY
        assert loaded.timing == SupplementTiming.PRE_WORKOUT
        assert loaded.notes == "Load phase done"

    def test_delete_supplement(self, storage: VaultStorage) -> None:
        s = Supplement(name="Test Supp", dosage="10mg")
        storage.save_supplement(s)
        assert len(storage.load_supplements()) >= 1
        storage.delete_supplement(s.supplement_id)
        ids = [sup.supplement_id for sup in storage.load_supplements()]
        assert s.supplement_id not in ids

    def test_supplements_sorted_by_name(self, storage: VaultStorage) -> None:
        s1 = Supplement(name="Zinc")
        s2 = Supplement(name="Creatine")
        storage.save_supplement(s1)
        storage.save_supplement(s2)
        supplements = storage.load_supplements()
        names = [s.name for s in supplements[-2:]]
        assert names == sorted(names)


# ── Monthly Progress ──


class TestMonthlyProgress:
    def test_append_progress_creates_file(self, storage: VaultStorage) -> None:
        w = Workout(
            date=date(2026, 6, 1),
            exercises=[
                Exercise(
                    name="Bench Press",
                    sets=[Set(weight=100, reps=5)],
                ),
            ],
        )
        storage.append_monthly_progress(w)
        progress_file = storage.config.gym_path / "Progress-2026-06.md"
        assert progress_file.exists()
        content = progress_file.read_text()
        assert "2026-06-01" in content
        assert "Bench Press" in content
        assert "100" in content

    def test_append_multiple_workouts(self, storage: VaultStorage) -> None:
        w1 = Workout(
            date=date(2026, 6, 1),
            exercises=[Exercise(name="Bench", sets=[Set(weight=100, reps=5)])],
        )
        w2 = Workout(
            date=date(2026, 6, 3),
            exercises=[Exercise(name="Squat", sets=[Set(weight=140, reps=5)])],
        )
        storage.append_monthly_progress(w1)
        storage.append_monthly_progress(w2)
        content = (storage.config.gym_path / "Progress-2026-06.md").read_text()
        assert content.count("2026-06-01") == 1
        assert content.count("2026-06-03") == 1
