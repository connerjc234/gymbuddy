"""Data models for workout tracker."""

import uuid
from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum


class UnitSystem(StrEnum):
    METRIC = "metric"
    IMPERIAL = "imperial"


@dataclass
class Set:
    weight: float
    reps: int
    rpe: float | None = None
    is_warmup: bool = False
    set_number: int = 0

    @property
    def volume(self) -> float:
        return self.weight * self.reps

    @property
    def estimated_1rm(self) -> float | None:
        if self.reps <= 0:
            return None
        return self.weight * (1 + self.reps / 30)


@dataclass
class Exercise:
    name: str
    sets: list[Set] = field(default_factory=list)
    notes: str = ""
    order: int = 0
    exercise_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    @property
    def total_volume(self) -> float:
        return sum(s.volume for s in self.sets if not s.is_warmup)

    @property
    def working_sets(self) -> list[Set]:
        return [s for s in self.sets if not s.is_warmup]

    @property
    def max_weight(self) -> float:
        working = self.working_sets
        return max((s.weight for s in working), default=0.0)

    @property
    def top_set(self) -> Set | None:
        working = self.working_sets
        return max(working, key=lambda s: s.weight) if working else None


@dataclass
class Workout:
    date: date
    exercises: list[Exercise] = field(default_factory=list)
    split_day: str | None = None
    duration_min: int | None = None
    notes: str = ""
    completed: bool = True
    workout_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    @property
    def total_volume(self) -> float:
        return sum(e.total_volume for e in self.exercises)

    @property
    def exercise_count(self) -> int:
        return len(self.exercises)

    @property
    def total_sets(self) -> int:
        return sum(len(e.working_sets) for e in self.exercises)


class GoalMetric(StrEnum):
    WEIGHT = "weight"
    REPS = "reps"
    VOLUME = "volume"
    BODYWEIGHT = "bodyweight"
    CONSISTENCY = "consistency"


@dataclass
class Goal:
    name: str
    target_date: date
    metric: GoalMetric
    target_value: float
    current_value: float = 0.0
    exercise_name: str | None = None
    goal_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    created_date: date = field(default_factory=date.today)
    notes: str = ""

    @property
    def days_remaining(self) -> int:
        return (self.target_date - date.today()).days

    @property
    def progress_pct(self) -> float:
        if self.target_value == 0:
            return 0.0
        return min(100.0, (self.current_value / self.target_value) * 100)

    @property
    def is_overdue(self) -> bool:
        return date.today() > self.target_date

    @property
    def is_complete(self) -> bool:
        return self.current_value >= self.target_value


@dataclass
class WorkoutTemplate:
    name: str
    exercises: list[Exercise] = field(default_factory=list)
    split_day: str | None = None
    notes: str = ""
    template_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    @property
    def exercise_count(self) -> int:
        return len(self.exercises)

    def to_workout(self, workout_date: date) -> Workout:
        return Workout(
            date=workout_date,
            exercises=[
                Exercise(
                    name=e.name,
                    order=i,
                    sets=[
                        Set(
                            weight=0,
                            reps=s.reps,
                            rpe=s.rpe,
                            is_warmup=s.is_warmup,
                            set_number=s.set_number,
                        )
                        for s in e.sets
                    ],
                )
                for i, e in enumerate(self.exercises)
            ],
            split_day=self.split_day,
            notes=self.notes,
        )


@dataclass
class UserProfile:
    name: str = "User"
    unit_system: UnitSystem = UnitSystem.METRIC
    bodyweight: float | None = None
    height_cm: float | None = None
    age: int | None = None
    experience_level: str = "intermediate"
