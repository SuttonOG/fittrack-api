"""CRUD endpoints for workout log entries.

Users can only log entries against their own workouts and can only
view / modify / delete their own log entries.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.workout import Workout
from app.models.workout_log import WorkoutLog
from app.models.exercise import Exercise
from app.schemas.workout_log import WorkoutLogCreate, WorkoutLogUpdate, WorkoutLogRead
from app.auth.jwt import get_current_user

router = APIRouter(prefix="/logs", tags=["Workout Logs"])


def _verify_ownership(db: Session, workout_id: int, user_id: int) -> Workout:
    """Ensure the workout belongs to the requesting user."""
    workout = (
        db.query(Workout)
        .filter(Workout.id == workout_id, Workout.user_id == user_id)
        .first()
    )
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found or not owned by you")
    return workout


@router.post("/", response_model=WorkoutLogRead, status_code=status.HTTP_201_CREATED)
def create_log(
    payload: WorkoutLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Log an exercise entry against one of your workouts."""
    _verify_ownership(db, payload.workout_id, current_user.id)

    if not db.query(Exercise).filter(Exercise.id == payload.exercise_id).first():
        raise HTTPException(status_code=404, detail="Exercise not found")

    log = WorkoutLog(**payload.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/", response_model=list[WorkoutLogRead])
def list_logs(
    workout_id: int | None = Query(None, description="Filter by workout"),
    exercise_id: int | None = Query(None, description="Filter by exercise"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List workout log entries for the authenticated user."""
    user_workout_ids = [
        w.id for w in db.query(Workout.id).filter(Workout.user_id == current_user.id).all()
    ]
    query = db.query(WorkoutLog).filter(WorkoutLog.workout_id.in_(user_workout_ids))

    if workout_id is not None:
        query = query.filter(WorkoutLog.workout_id == workout_id)
    if exercise_id is not None:
        query = query.filter(WorkoutLog.exercise_id == exercise_id)

    return query.order_by(WorkoutLog.logged_at.desc()).offset(skip).limit(limit).all()


@router.get("/{log_id}", response_model=WorkoutLogRead)
def get_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve a single workout log entry."""
    log = db.query(WorkoutLog).filter(WorkoutLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log entry not found")

    _verify_ownership(db, log.workout_id, current_user.id)
    return log


@router.put("/{log_id}", response_model=WorkoutLogRead)
def update_log(
    log_id: int,
    payload: WorkoutLogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a workout log entry."""
    log = db.query(WorkoutLog).filter(WorkoutLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log entry not found")

    _verify_ownership(db, log.workout_id, current_user.id)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(log, field, value)

    db.commit()
    db.refresh(log)
    return log


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a workout log entry."""
    log = db.query(WorkoutLog).filter(WorkoutLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log entry not found")

    _verify_ownership(db, log.workout_id, current_user.id)
    db.delete(log)
    db.commit()
