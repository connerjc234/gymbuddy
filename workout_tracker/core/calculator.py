"""Calculation utilities for workout tracker."""

from .models import Exercise, Workout


def epley_1rm(weight: float, reps: int) -> float:
    if reps <= 1:
        return weight
    return weight * (1 + reps / 30)


def brzycki_1rm(weight: float, reps: int) -> float:
    if reps <= 1:
        return weight
    return weight * (36 / (37 - reps))


def estimate_1rm(weight: float, reps: int, method: str = "epley") -> float:
    if method == "brzycki":
        return brzycki_1rm(weight, reps)
    return epley_1rm(weight, reps)


def rep_max_from_1rm(one_rm: float, reps: int, method: str = "epley") -> float:
    if reps <= 1:
        return one_rm
    if method == "brzycki":
        return one_rm * (37 - reps) / 36
    return one_rm / (1 + reps / 30)


def rpe_to_rir(rpe: float) -> int:
    return max(0, int(round(10 - rpe)))


def rir_to_rpe(rir: int) -> float:
    return 10 - rir


def calculate_session_volume(workout: Workout) -> float:
    return sum(ex.total_volume for ex in workout.exercises)


def calculate_exercise_1rm_estimates(
    exercise: Exercise,
) -> list[tuple[float, int, float]]:
    results = []
    for s in exercise.working_sets:
        est = epley_1rm(s.weight, s.reps)
        results.append((s.weight, s.reps, est))
    return results


def best_estimated_1rm(exercise: Exercise) -> float | None:
    estimates = calculate_exercise_1rm_estimates(exercise)
    return max((e[2] for e in estimates), default=None)


def suggest_progression(
    exercise: Exercise, target_rpe: float = 8.0, increment: float = 2.5
) -> float | None:
    top = exercise.top_set
    if not top:
        return None

    est_1rm = epley_1rm(top.weight, top.reps)
    target_weight = rep_max_from_1rm(est_1rm, top.reps)

    if top.rpe is not None and top.rpe < target_rpe:
        return round(target_weight + increment, 1)
    elif top.rpe is not None and top.rpe > target_rpe:
        return round(target_weight - increment, 1)
    return round(target_weight, 1)


def weekly_volume(workouts: list[Workout], exercise_name: str) -> dict[int, float]:
    from collections import defaultdict

    vol_by_week: dict[int, float] = defaultdict(float)
    for w in workouts:
        for ex in w.exercises:
            if ex.name.lower() == exercise_name.lower():
                week = w.date.isocalendar()[1]
                vol_by_week[week] += ex.total_volume
    return dict(sorted(vol_by_week.items()))


def consistency_streak(workouts: list[Workout]) -> int:
    if not workouts:
        return 0
    dates = sorted(set(w.date for w in workouts))
    streak = 1
    for i in range(len(dates) - 1, 0, -1):
        if (dates[i] - dates[i - 1]).days == 1:
            streak += 1
        else:
            break
    return streak
