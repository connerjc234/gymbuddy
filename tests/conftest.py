"""Shared fixtures for workout tracker tests."""

from collections.abc import Generator
from datetime import date
from pathlib import Path
from typing import Any

import pytest

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


@pytest.fixture
def sample_set() -> Set:
    return Set(weight=100.0, reps=5, rpe=8.0, set_number=1)


@pytest.fixture
def sample_warmup_set() -> Set:
    return Set(weight=60.0, reps=5, is_warmup=True, set_number=1)


@pytest.fixture
def sample_exercise(sample_set: Set, sample_warmup_set: Set) -> Exercise:
    return Exercise(
        name="Bench Press",
        order=0,
        sets=[sample_warmup_set, sample_set],
        notes="Feel good",
    )


@pytest.fixture
def sample_workout(sample_exercise: Exercise) -> Workout:
    return Workout(
        date=date(2026, 6, 1),
        exercises=[sample_exercise],
        split_day="Push",
        duration_min=45,
        notes="Great session",
    )


@pytest.fixture
def sample_goal() -> Goal:
    return Goal(
        name="Bench 225",
        target_date=date(2026, 8, 15),
        metric=GoalMetric.WEIGHT,
        target_value=225.0,
        current_value=185.0,
        exercise_name="Bench Press",
    )


@pytest.fixture
def sample_template(sample_exercise: Exercise) -> WorkoutTemplate:
    return WorkoutTemplate(
        name="Push Day",
        exercises=[sample_exercise],
        split_day="Push",
        notes="Standard push workout",
    )


@pytest.fixture
def sample_supplement() -> Supplement:
    return Supplement(
        name="Creatine",
        dosage="5g",
        frequency=SupplementFrequency.DAILY,
        timing=SupplementTiming.PRE_WORKOUT,
    )


@pytest.fixture
def temp_vault(tmp_path: Path) -> Generator[Path, Any, None]:
    """Create a temporary vault directory with Gym subdirectories."""
    vault = tmp_path / "ObsidianVault"
    gym = vault / "Gym"
    (gym / "Workouts").mkdir(parents=True)
    (gym / "Goals").mkdir(parents=True)
    (gym / "Templates").mkdir(parents=True)
    (gym / "Supplements").mkdir(parents=True)
    (gym / "AI-Notes").mkdir(parents=True)
    yield vault


@pytest.fixture
def two_workouts() -> list[Workout]:
    """Two consecutive days of workouts for streak/volume tests."""
    return [
        Workout(
            date=date(2026, 6, 1),
            exercises=[
                Exercise(
                    name="Bench Press",
                    sets=[Set(weight=100, reps=5), Set(weight=90, reps=8)],
                    order=0,
                ),
                Exercise(
                    name="Squat",
                    sets=[Set(weight=140, reps=5)],
                    order=1,
                ),
            ],
            split_day="Push",
        ),
        Workout(
            date=date(2026, 6, 2),
            exercises=[
                Exercise(
                    name="Bench Press",
                    sets=[Set(weight=102.5, reps=5)],
                    order=0,
                ),
            ],
            split_day="Push",
        ),
    ]
