"""CRUD endpoints for the exercise catalogue.

Exercises are a shared resource (not user-scoped) so any authenticated user
can create, read, update, or delete them.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.exercise import Exercise
from app.models.user import User
from app.schemas.exercise import ExerciseCreate, ExerciseUpdate, ExerciseRead
from app.auth.jwt import get_current_user

router = APIRouter(prefix="/exercises", tags=["Exercises"])


@router.post("/", response_model=ExerciseRead, status_code=status.HTTP_201_CREATED)
def create_exercise(
    payload: ExerciseCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Add a new exercise to the catalogue."""
    if db.query(Exercise).filter(Exercise.name == payload.name).first():
        raise HTTPException(status_code=409, detail="Exercise with this name already exists")

    exercise = Exercise(**payload.model_dump())
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return exercise


@router.get("/", response_model=list[ExerciseRead])
def list_exercises(
    muscle_group: Optional[str] = Query(None, description="Filter by muscle group"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List exercises with optional filters. No authentication required."""
    query = db.query(Exercise)
    if muscle_group:
        query = query.filter(Exercise.muscle_group.ilike(f"%{muscle_group}%"))
    if difficulty:
        query = query.filter(Exercise.difficulty.ilike(difficulty))
    return query.offset(skip).limit(limit).all()


@router.get("/{exercise_id}", response_model=ExerciseRead)
def get_exercise(exercise_id: int, db: Session = Depends(get_db)):
    """Retrieve a single exercise by its ID."""
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return exercise


@router.put("/{exercise_id}", response_model=ExerciseRead)
def update_exercise(
    exercise_id: int,
    payload: ExerciseUpdate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Update an existing exercise's details."""
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(exercise, field, value)

    db.commit()
    db.refresh(exercise)
    return exercise


@router.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise(
    exercise_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Remove an exercise from the catalogue."""
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    db.delete(exercise)
    db.commit()
