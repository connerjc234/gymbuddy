"""Characterization tests for data models.

These tests pin the current behavior of Set, Exercise, Workout, Goal,
WorkoutTemplate, and Supplement dataclasses before any refactoring.
"""

from datetime import date, datetime

from workout_tracker.core.models import (
    Exercise,
    Goal,
    GoalMetric,
    Set,
    Supplement,
    SupplementFrequency,
    Workout,
    WorkoutTemplate,
)

# ── Set ──


class TestSet:
    def test_volume_computed(self) -> None:
        s = Set(weight=100, reps=5)
        assert s.volume == 500.0

    def test_volume_zero_weight(self) -> None:
        s = Set(weight=0, reps=10)
        assert s.volume == 0.0

    def test_estimated_1rm(self) -> None:
        s = Set(weight=100, reps=5)
        assert s.estimated_1rm is not None
        assert abs(s.estimated_1rm - 116.67) < 0.01

    def test_estimated_1rm_zero_reps(self) -> None:
        s = Set(weight=100, reps=0)
        assert s.estimated_1rm is None

    def test_estimated_1rm_single_rep(self) -> None:
        """Current formula: weight * (1 + reps/30), even for single rep."""
        s = Set(weight=150, reps=1)
        # 150 * (1 + 1/30) ≈ 155.0
        assert s.estimated_1rm is not None
        assert abs(s.estimated_1rm - 155.0) < 0.01

    def test_defaults(self) -> None:
        s = Set(weight=50, reps=10)
        assert s.rpe is None
        assert not s.is_warmup
        assert s.set_number == 0

    def test_warmup_excluded_from_volume_in_exercise(self) -> None:
        """Warmup sets are excluded from Exercise.total_volume."""
        ex = Exercise(
            name="Bench",
            sets=[
                Set(weight=60, reps=5, is_warmup=True),
                Set(weight=100, reps=5),
            ],
        )
        assert ex.total_volume == 500.0  # Only working set

    def test_working_sets_filter(self) -> None:
        ex = Exercise(
            name="Bench",
            sets=[
                Set(weight=60, reps=5, is_warmup=True),
                Set(weight=100, reps=5),
            ],
        )
        assert len(ex.working_sets) == 1
        assert ex.working_sets[0].weight == 100

    def test_max_weight(self) -> None:
        ex = Exercise(
            name="Bench",
            sets=[
                Set(weight=60, reps=5, is_warmup=True),
                Set(weight=100, reps=5),
                Set(weight=110, reps=3),
            ],
        )
        assert ex.max_weight == 110.0

    def test_top_set_heaviest_working(self) -> None:
        ex = Exercise(
            name="Bench",
            sets=[
                Set(weight=60, reps=5, is_warmup=True),
                Set(weight=100, reps=5),
                Set(weight=110, reps=3),
            ],
        )
        assert ex.top_set is not None
        assert ex.top_set.weight == 110.0

    def test_top_set_none_when_only_warmup(self) -> None:
        ex = Exercise(name="Bench", sets=[Set(weight=60, reps=5, is_warmup=True)])
        assert ex.top_set is None

    def test_exercise_id_generated(self) -> None:
        ex = Exercise(name="Squat")
        assert len(ex.exercise_id) == 8


# ── Workout ──


class TestWorkout:
    def test_total_volume(self, sample_workout: Workout) -> None:
        # Bench Press: 60x5 warmup (excluded) + 100x5 working = 500
        assert sample_workout.total_volume == 500.0

    def test_exercise_count(self, sample_workout: Workout) -> None:
        assert sample_workout.exercise_count == 1

    def test_total_sets(self, sample_workout: Workout) -> None:
        # 1 working set (warmup excluded)
        assert sample_workout.total_sets == 1

    def test_default_completed(self) -> None:
        w = Workout(date=date.today())
        assert w.completed

    def test_workout_id_generated(self) -> None:
        w = Workout(date=date.today())
        assert len(w.workout_id) == 8

    def test_multi_exercise_volume(self) -> None:
        w = Workout(
            date=date.today(),
            exercises=[
                Exercise(
                    name="Bench",
                    sets=[Set(weight=100, reps=5)],
                ),
                Exercise(
                    name="Squat",
                    sets=[Set(weight=140, reps=5)],
                ),
            ],
        )
        assert w.total_volume == 500.0 + 700.0

    def test_empty_exercises(self) -> None:
        w = Workout(date=date.today())
        assert w.total_volume == 0.0
        assert w.exercise_count == 0
        assert w.total_sets == 0


# ── Goal ──


class TestGoal:
    def test_days_remaining_future(self) -> None:
        g = Goal(
            name="Test",
            target_date=date(2099, 12, 31),
            metric=GoalMetric.WEIGHT,
            target_value=100,
        )
        assert g.days_remaining > 0

    def test_days_remaining_past(self) -> None:
        g = Goal(
            name="Test",
            target_date=date(2020, 1, 1),
            metric=GoalMetric.WEIGHT,
            target_value=100,
        )
        assert g.days_remaining < 0

    def test_progress_pct_partial(self) -> None:
        g = Goal(
            name="Test",
            target_date=date(2099, 12, 31),
            metric=GoalMetric.WEIGHT,
            target_value=200,
            current_value=100,
        )
        assert g.progress_pct == 50.0

    def test_progress_pct_complete(self) -> None:
        g = Goal(
            name="Test",
            target_date=date(2099, 12, 31),
            metric=GoalMetric.WEIGHT,
            target_value=200,
            current_value=200,
        )
        assert g.progress_pct == 100.0

    def test_progress_pct_over_target(self) -> None:
        g = Goal(
            name="Test",
            target_date=date(2099, 12, 31),
            metric=GoalMetric.WEIGHT,
            target_value=200,
            current_value=250,
        )
        assert g.progress_pct == 100.0  # Capped at 100

    def test_progress_pct_zero_target(self) -> None:
        g = Goal(
            name="Test",
            target_date=date(2099, 12, 31),
            metric=GoalMetric.WEIGHT,
            target_value=0,
            current_value=0,
        )
        assert g.progress_pct == 0.0

    def test_is_overdue(self) -> None:
        g = Goal(
            name="Test",
            target_date=date(2020, 1, 1),
            metric=GoalMetric.WEIGHT,
            target_value=100,
        )
        assert g.is_overdue

    def test_is_not_overdue(self) -> None:
        g = Goal(
            name="Test",
            target_date=date(2099, 12, 31),
            metric=GoalMetric.WEIGHT,
            target_value=100,
        )
        assert not g.is_overdue

    def test_is_complete(self) -> None:
        g = Goal(
            name="Test",
            target_date=date(2099, 12, 31),
            metric=GoalMetric.WEIGHT,
            target_value=100,
            current_value=100,
        )
        assert g.is_complete

    def test_is_not_complete(self) -> None:
        g = Goal(
            name="Test",
            target_date=date(2099, 12, 31),
            metric=GoalMetric.WEIGHT,
            target_value=100,
            current_value=50,
        )
        assert not g.is_complete

    def test_goal_id_generated(self) -> None:
        g = Goal(
            name="Test",
            target_date=date(2099, 12, 31),
            metric=GoalMetric.WEIGHT,
            target_value=100,
        )
        assert len(g.goal_id) == 8

    def test_created_date_defaults_today(self) -> None:
        g = Goal(
            name="Test",
            target_date=date(2099, 12, 31),
            metric=GoalMetric.WEIGHT,
            target_value=100,
        )
        assert g.created_date == date.today()

    def test_metric_enum_values(self) -> None:
        assert GoalMetric.WEIGHT.value == "weight"
        assert GoalMetric.REPS.value == "reps"
        assert GoalMetric.VOLUME.value == "volume"
        assert GoalMetric.BODYWEIGHT.value == "bodyweight"
        assert GoalMetric.CONSISTENCY.value == "consistency"


# ── WorkoutTemplate ──


class TestWorkoutTemplate:
    def test_to_workout_creates_new_workout(self) -> None:
        t = WorkoutTemplate(
            name="Push Day",
            exercises=[
                Exercise(
                    name="Bench Press",
                    sets=[Set(weight=0, reps=8, rpe=7.0, set_number=1)],
                    order=0,
                ),
            ],
            split_day="Push",
        )
        w = t.to_workout(date(2026, 6, 15))
        assert isinstance(w, Workout)
        assert w.date == date(2026, 6, 15)
        assert w.split_day == "Push"
        assert len(w.exercises) == 1
        assert w.exercises[0].name == "Bench Press"
        assert w.exercises[0].sets[0].weight == 0  # Template weight zeroed

    def test_exercise_count(self) -> None:
        t = WorkoutTemplate(
            name="Full Body",
            exercises=[
                Exercise(name="Squat", order=0),
                Exercise(name="Bench", order=1),
                Exercise(name="Row", order=2),
            ],
        )
        assert t.exercise_count == 3

    def test_template_id_generated(self) -> None:
        t = WorkoutTemplate(name="Test")
        assert len(t.template_id) == 8


# ── Supplement ──


class TestSupplement:
    def test_is_due_daily(self) -> None:
        s = Supplement(
            name="Creatine",
            frequency=SupplementFrequency.DAILY,
        )
        assert s.is_due_today

    def test_not_due_when_disabled(self) -> None:
        s = Supplement(
            name="Creatine",
            frequency=SupplementFrequency.DAILY,
            enabled=False,
        )
        assert not s.is_due_today

    def test_not_taken_initially(self) -> None:
        s = Supplement(name="Creatine")
        assert not s.is_taken_today

    def test_mark_taken(self) -> None:
        s = Supplement(name="Creatine")
        s.mark_taken()
        assert s.is_taken_today
        assert s.last_taken is not None
        assert s.last_taken.date() == date.today()

    def test_mark_taken_with_time(self) -> None:
        s = Supplement(name="Creatine")
        dt = datetime(2026, 6, 1, 8, 0)
        s.mark_taken(dt)
        assert s.last_taken == dt
