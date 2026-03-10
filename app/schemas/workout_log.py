"""Pydantic schemas for workout log entries."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class WorkoutLogCreate(BaseModel):
    workout_id: int = Field(..., examples=[1])
    exercise_id: int = Field(..., examples=[1])
    sets: int = Field(..., ge=1, examples=[4])
    reps: int = Field(..., ge=1, examples=[10])
    weight_kg: Optional[float] = Field(None, ge=0, examples=[80.0])
    duration_minutes: Optional[float] = Field(None, ge=0, examples=[5.5])
    notes: Optional[str] = Field(None, examples=["Felt strong today"])


class WorkoutLogUpdate(BaseModel):
    sets: Optional[int] = Field(None, ge=1)
    reps: Optional[int] = Field(None, ge=1)
    weight_kg: Optional[float] = Field(None, ge=0)
    duration_minutes: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None


class WorkoutLogRead(BaseModel):
    id: int
    workout_id: int
    exercise_id: int
    sets: int
    reps: int
    weight_kg: Optional[float]
    duration_minutes: Optional[float]
    notes: Optional[str]
    logged_at: datetime

    model_config = {"from_attributes": True}
