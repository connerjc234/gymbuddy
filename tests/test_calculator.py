"""Characterization tests for calculator utilities.

Pins current behavior of 1RM estimation, volume, progression suggestions,
and consistency streak calculations before any refactoring.
"""

from datetime import date

from workout_tracker.core.calculator import (
    best_estimated_1rm,
    brzycki_1rm,
    calculate_exercise_1rm_estimates,
    calculate_session_volume,
    consistency_streak,
    epley_1rm,
    estimate_1rm,
    rep_max_from_1rm,
    rir_to_rpe,
    rpe_to_rir,
    suggest_progression,
    weekly_volume,
)
from workout_tracker.core.models import Exercise, Set, Workout


class TestEpley1RM:
    def test_single_rep(self) -> None:
        assert epley_1rm(100, 1) == 100.0

    def test_multi_rep(self) -> None:
        result = epley_1rm(100, 5)
        assert abs(result - 116.67) < 0.01

    def test_high_reps(self) -> None:
        result = epley_1rm(100, 10)
        assert abs(result - 133.33) < 0.01


class TestBrzycki1RM:
    def test_single_rep(self) -> None:
        assert brzycki_1rm(100, 1) == 100.0

    def test_multi_rep(self) -> None:
        result = brzycki_1rm(100, 5)
        assert abs(result - 112.5) < 0.01

    def test_high_reps(self) -> None:
        result = brzycki_1rm(100, 10)
        assert abs(result - 133.33) < 0.01


class TestEstimate1RM:
    def test_default_method(self) -> None:
        result = estimate_1rm(100, 5)
        assert abs(result - 116.67) < 0.01

    def test_brzycki_method(self) -> None:
        result = estimate_1rm(100, 5, method="brzycki")
        assert abs(result - 112.5) < 0.01


class TestRepMaxFrom1RM:
    def test_epley_rep_max(self) -> None:
        result = rep_max_from_1rm(116.67, 5)
        assert abs(result - 100.0) < 1.0

    def test_single_rep(self) -> None:
        assert rep_max_from_1rm(100, 1) == 100.0

    def test_brzycki_rep_max(self) -> None:
        result = rep_max_from_1rm(112.5, 5, method="brzycki")
        assert abs(result - 100.0) < 1.0


class TestRPEConversions:
    def test_rpe_to_rir(self) -> None:
        assert rpe_to_rir(8.0) == 2
        assert rpe_to_rir(10.0) == 0
        assert rpe_to_rir(7.5) == 2  # round(2.5) = 2

    def test_rir_to_rpe(self) -> None:
        assert rir_to_rpe(2) == 8.0
        assert rir_to_rpe(0) == 10.0

    def test_roundtrip_for_integer_rpe(self) -> None:
        """rpe_to_rir uses round(), so .5 values lose precision on roundtrip."""
        for rpe in [7.0, 8.0, 9.0, 10.0]:
            assert rir_to_rpe(rpe_to_rir(rpe)) == rpe

    def test_rpe_to_rir_rounds_to_nearest_int(self) -> None:
        assert rpe_to_rir(8.5) == 2  # round(1.5) = 2
        assert rpe_to_rir(8.4) == 2  # round(1.6) = 2


class TestCalculateSessionVolume:
    def test_empty_workout(self) -> None:
        w = Workout(date=date.today())
        assert calculate_session_volume(w) == 0.0

    def test_with_exercises(self) -> None:
        w = Workout(
            date=date.today(),
            exercises=[
                Exercise(
                    name="Bench",
                    sets=[Set(weight=100, reps=5)],
                ),
            ],
        )
        assert calculate_session_volume(w) == 500.0

    def test_warmup_excluded(self) -> None:
        w = Workout(
            date=date.today(),
            exercises=[
                Exercise(
                    name="Bench",
                    sets=[
                        Set(weight=60, reps=5, is_warmup=True),
                        Set(weight=100, reps=5),
                    ],
                ),
            ],
        )
        assert calculate_session_volume(w) == 500.0


class TestCalculateExercise1RMEstimates:
    def test_working_sets_only(self) -> None:
        ex = Exercise(
            name="Bench",
            sets=[
                Set(weight=60, reps=5, is_warmup=True),
                Set(weight=100, reps=5),
            ],
        )
        estimates = calculate_exercise_1rm_estimates(ex)
        assert len(estimates) == 1
        weight, reps, est = estimates[0]
        assert weight == 100
        assert reps == 5
        assert abs(est - 116.67) < 0.01


class TestBestEstimated1RM:
    def test_best_from_multiple_sets(self) -> None:
        ex = Exercise(
            name="Bench",
            sets=[
                Set(weight=100, reps=5),
                Set(weight=110, reps=3),
            ],
        )
        best = best_estimated_1rm(ex)
        assert best is not None
        # 110x3 = 121, 100x5 = 116.67 → best is 121
        assert abs(best - 121.0) < 0.01

    def test_none_when_no_sets(self) -> None:
        ex = Exercise(name="Bench")
        assert best_estimated_1rm(ex) is None


class TestSuggestProgression:
    def test_increase_when_below_target_rpe(self) -> None:
        ex = Exercise(
            name="Bench",
            sets=[Set(weight=100, reps=5, rpe=7.0)],
        )
        suggestion = suggest_progression(ex, target_rpe=8.0)
        assert suggestion is not None
        # Below target RPE → increase
        assert suggestion > 100.0

    def test_decrease_when_above_target_rpe(self) -> None:
        ex = Exercise(
            name="Bench",
            sets=[Set(weight=100, reps=5, rpe=9.5)],
        )
        suggestion = suggest_progression(ex, target_rpe=8.0)
        assert suggestion is not None
        # Above target RPE → decrease
        assert suggestion < 100.0

    def test_none_when_no_top_set(self) -> None:
        ex = Exercise(name="Bench")
        assert suggest_progression(ex) is None


class TestWeeklyVolume:
    def test_volume_by_week(self, two_workouts: list[Workout]) -> None:
        vol = weekly_volume(two_workouts, "Bench Press")
        assert len(vol) >= 1
        # Week 23 (June 1-2, 2026)
        week_num = date(2026, 6, 1).isocalendar()[1]
        assert week_num in vol
        # 100x5=500 + 90x8=720 + 102.5x5=512.5 = 1732.5
        assert abs(vol[week_num] - 1732.5) < 0.1

    def test_no_matches(self, two_workouts: list[Workout]) -> None:
        vol = weekly_volume(two_workouts, "Deadlift")
        assert vol == {}


class TestConsistencyStreak:
    def test_streak_consecutive_days(self) -> None:
        workouts = [
            Workout(date=date(2026, 6, 1)),
            Workout(date=date(2026, 6, 2)),
            Workout(date=date(2026, 6, 3)),
        ]
        assert consistency_streak(workouts) == 3

    def test_streak_with_gap(self) -> None:
        workouts = [
            Workout(date=date(2026, 6, 1)),
            Workout(date=date(2026, 6, 2)),
            Workout(date=date(2026, 6, 5)),
        ]
        assert consistency_streak(workouts) == 1  # Only 6/5 is the streak tail

    def test_single_workout(self) -> None:
        workouts = [Workout(date=date(2026, 6, 1))]
        assert consistency_streak(workouts) == 1

    def test_empty(self) -> None:
        assert consistency_streak([]) == 0

    def test_unsorted_dates(self) -> None:
        workouts = [
            Workout(date=date(2026, 6, 3)),
            Workout(date=date(2026, 6, 1)),
            Workout(date=date(2026, 6, 2)),
        ]
        assert consistency_streak(workouts) == 3

    def test_non_consecutive_recent(self) -> None:
        workouts = [
            Workout(date=date(2026, 5, 30)),
            Workout(date=date(2026, 5, 31)),
            Workout(date=date(2026, 6, 2)),
        ]
        # Streak starts from most recent: 6/2 only → 1
        assert consistency_streak(workouts) == 1
