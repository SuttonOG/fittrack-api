"""CRUD endpoints for user workout plans.

Workouts are scoped to the authenticated user: a user can only see, modify,
and delete their own workout plans.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.workout import Workout
from app.schemas.workout import WorkoutCreate, WorkoutUpdate, WorkoutRead
from app.auth.jwt import get_current_user

router = APIRouter(prefix="/workouts", tags=["Workouts"])


@router.post("/", response_model=WorkoutRead, status_code=status.HTTP_201_CREATED)
def create_workout(
    payload: WorkoutCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new workout plan for the authenticated user."""
    workout = Workout(**payload.model_dump(), user_id=current_user.id)
    db.add(workout)
    db.commit()
    db.refresh(workout)
    return workout


@router.get("/", response_model=list[WorkoutRead])
def list_workouts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all workout plans belonging to the authenticated user."""
    return (
        db.query(Workout)
        .filter(Workout.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{workout_id}", response_model=WorkoutRead)
def get_workout(
    workout_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve a specific workout plan owned by the authenticated user."""
    workout = (
        db.query(Workout)
        .filter(Workout.id == workout_id, Workout.user_id == current_user.id)
        .first()
    )
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    return workout


@router.put("/{workout_id}", response_model=WorkoutRead)
def update_workout(
    workout_id: int,
    payload: WorkoutUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a workout plan owned by the authenticated user."""
    workout = (
        db.query(Workout)
        .filter(Workout.id == workout_id, Workout.user_id == current_user.id)
        .first()
    )
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(workout, field, value)

    db.commit()
    db.refresh(workout)
    return workout


@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(
    workout_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a workout plan owned by the authenticated user."""
    workout = (
        db.query(Workout)
        .filter(Workout.id == workout_id, Workout.user_id == current_user.id)
        .first()
    )
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    db.delete(workout)
    db.commit()
