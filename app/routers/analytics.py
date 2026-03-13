"""Analytics endpoints providing fitness insights derived from workout logs.

These read-only endpoints compute personal records, training volume trends,
muscle-group distribution, and workout streaks for the authenticated user.
"""

from collections import defaultdict
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.user import User
from app.models.workout import Workout
from app.models.workout_log import WorkoutLog
from app.models.exercise import Exercise
from app.models.benchmark import Benchmark
from app.auth.jwt import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def _user_log_query(db: Session, user_id: int):
    """Base query: all WorkoutLog rows belonging to the given user."""
    return (
        db.query(WorkoutLog)
        .join(Workout, WorkoutLog.workout_id == Workout.id)
        .filter(Workout.user_id == user_id)
    )


# ------------------------------------------------------------------
# 1. Personal Records
# ------------------------------------------------------------------

@router.get("/personal-records")
def personal_records(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return the heaviest single-set lift per exercise for the user.

    Response: list of {exercise_id, exercise_name, best_weight_kg, reps, logged_at}
    """
    logs = _user_log_query(db, current_user.id).all()

    best: dict[int, WorkoutLog] = {}
    for log in logs:
        if log.weight_kg is not None:
            current_best = best.get(log.exercise_id)
            if current_best is None or log.weight_kg > current_best.weight_kg:
                best[log.exercise_id] = log

    records = []
    for exercise_id, log in best.items():
        exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        records.append({
            "exercise_id": exercise_id,
            "exercise_name": exercise.name if exercise else "Unknown",
            "best_weight_kg": log.weight_kg,
            "reps": log.reps,
            "logged_at": log.logged_at.isoformat() if log.logged_at else None,
        })

    return {"personal_records": sorted(records, key=lambda r: r["best_weight_kg"], reverse=True)}


# ------------------------------------------------------------------
# 2. Volume Trends
# ------------------------------------------------------------------

@router.get("/volume-trends")
def volume_trends(
    period: str = Query("weekly", regex="^(weekly|monthly)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Total training volume (sets x reps x weight_kg) grouped by week or month.

    Query params:
        period: 'weekly' | 'monthly'

    Response: list of {period_label, total_volume_kg, total_sets, total_reps}
    """
    logs = _user_log_query(db, current_user.id).order_by(WorkoutLog.logged_at).all()

    buckets: dict[str, dict] = defaultdict(lambda: {"total_volume_kg": 0.0, "total_sets": 0, "total_reps": 0})

    for log in logs:
        if log.logged_at is None:
            continue
        if period == "weekly":
            label = log.logged_at.strftime("%G-W%V")  # ISO week
        else:
            label = log.logged_at.strftime("%Y-%m")

        weight = log.weight_kg or 0
        buckets[label]["total_volume_kg"] += log.sets * log.reps * weight
        buckets[label]["total_sets"] += log.sets
        buckets[label]["total_reps"] += log.sets * log.reps

    trends = [
        {"period_label": label, **data}
        for label, data in sorted(buckets.items())
    ]
    return {"period": period, "trends": trends}


# ------------------------------------------------------------------
# 3. Muscle-Group Distribution
# ------------------------------------------------------------------

@router.get("/muscle-group-distribution")
def muscle_group_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Proportion of total sets dedicated to each muscle group.

    Useful for rendering a pie/donut chart on a frontend client.

    Response: list of {muscle_group, total_sets, percentage}
    """
    logs = _user_log_query(db, current_user.id).all()

    group_sets: dict[str, int] = defaultdict(int)
    total = 0
    for log in logs:
        exercise = db.query(Exercise).filter(Exercise.id == log.exercise_id).first()
        if exercise:
            group_sets[exercise.muscle_group] += log.sets
            total += log.sets

    distribution = [
        {
            "muscle_group": group,
            "total_sets": sets,
            "percentage": round(sets / total * 100, 1) if total else 0,
        }
        for group, sets in sorted(group_sets.items(), key=lambda x: x[1], reverse=True)
    ]
    return {"total_sets": total, "distribution": distribution}


# ------------------------------------------------------------------
# 4. Workout Streak
# ------------------------------------------------------------------

@router.get("/streak")
def workout_streak(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Current and longest consecutive-day workout streaks.

    A 'workout day' is any calendar date on which at least one log entry exists.

    Response: {current_streak_days, longest_streak_days, total_workout_days}
    """
    logs = _user_log_query(db, current_user.id).order_by(WorkoutLog.logged_at).all()

    # Collect unique dates
    dates = sorted({log.logged_at.date() for log in logs if log.logged_at})

    if not dates:
        return {"current_streak_days": 0, "longest_streak_days": 0, "total_workout_days": 0}

    longest = 1
    current = 1
    for i in range(1, len(dates)):
        if (dates[i] - dates[i - 1]).days == 1:
            current += 1
            longest = max(longest, current)
        else:
            current = 1

    # Check if the streak is still active (last workout was today or yesterday)
    today = datetime.now(timezone.utc).date()
    if (today - dates[-1]).days > 1:
        current = 0

    return {
        "current_streak_days": current,
        "longest_streak_days": longest,
        "total_workout_days": len(dates),
    }


# ------------------------------------------------------------------
# 5. Strength Benchmarks — compare PRs against population data
# ------------------------------------------------------------------

@router.get("/benchmarks")
def strength_benchmarks(
    gender: str = Query(..., pattern="^(male|female)$", description="Your gender"),
    bodyweight_kg: float = Query(..., gt=0, description="Your bodyweight in kg"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Compare the user's personal records against population strength standards.

    For each exercise where the user has logged a weight and a matching
    benchmark exists, returns the user's classification (beginner → elite)
    and an estimated percentile.

    Query params:
        gender: 'male' | 'female'
        bodyweight_kg: user's current bodyweight in kilograms
    """
    # Get user's PRs
    logs = _user_log_query(db, current_user.id).all()
    best: dict[str, float] = {}
    for log in logs:
        if log.weight_kg is not None:
            exercise = db.query(Exercise).filter(Exercise.id == log.exercise_id).first()
            if exercise:
                current_best = best.get(exercise.name, 0)
                if log.weight_kg > current_best:
                    best[exercise.name] = log.weight_kg

    if not best:
        return {"gender": gender, "bodyweight_kg": bodyweight_kg, "comparisons": []}

    # Find the closest bodyweight bracket for each exercise
    comparisons = []
    for exercise_name, user_weight in best.items():
        benchmarks = (
            db.query(Benchmark)
            .filter(Benchmark.exercise_name == exercise_name, Benchmark.gender == gender)
            .all()
        )
        if not benchmarks:
            continue

        # Pick the closest bodyweight row
        closest = min(benchmarks, key=lambda b: abs(b.bodyweight_kg - bodyweight_kg))

        # Determine classification and estimated percentile
        levels = [
            ("beginner", closest.beginner_kg, 20),
            ("novice", closest.novice_kg, 40),
            ("intermediate", closest.intermediate_kg, 60),
            ("advanced", closest.advanced_kg, 80),
            ("elite", closest.elite_kg, 95),
        ]

        classification = "below beginner"
        percentile = 5
        for level_name, threshold, pct in levels:
            if user_weight >= threshold:
                classification = level_name
                percentile = pct

        # Interpolate percentile within the bracket for more accuracy
        for i, (level_name, threshold, pct) in enumerate(levels):
            if user_weight < threshold:
                if i == 0:
                    percentile = round(user_weight / threshold * 20, 1)
                else:
                    prev_threshold = levels[i - 1][1]
                    prev_pct = levels[i - 1][2]
                    ratio = (user_weight - prev_threshold) / (threshold - prev_threshold)
                    percentile = round(prev_pct + ratio * (pct - prev_pct), 1)
                break

        comparisons.append({
            "exercise_name": exercise_name,
            "your_pr_kg": user_weight,
            "classification": classification,
            "estimated_percentile": min(percentile, 99.9),
            "benchmark_bodyweight_kg": closest.bodyweight_kg,
            "standards": {
                "beginner": closest.beginner_kg,
                "novice": closest.novice_kg,
                "intermediate": closest.intermediate_kg,
                "advanced": closest.advanced_kg,
                "elite": closest.elite_kg,
            },
        })

    comparisons.sort(key=lambda c: c["estimated_percentile"], reverse=True)
    return {"gender": gender, "bodyweight_kg": bodyweight_kg, "comparisons": comparisons}