"""Pydantic schemas for exercise CRUD operations."""

from typing import Optional
from pydantic import BaseModel, Field


class ExerciseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["Barbell Bench Press"])
    muscle_group: str = Field(..., max_length=50, examples=["chest"])
    equipment: Optional[str] = Field(None, max_length=50, examples=["barbell"])
    difficulty: str = Field("intermediate", examples=["beginner"])
    description: Optional[str] = Field(None, examples=["Flat bench press with barbell"])


class ExerciseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    muscle_group: Optional[str] = Field(None, max_length=50)
    equipment: Optional[str] = None
    difficulty: Optional[str] = None
    description: Optional[str] = None


class ExerciseRead(BaseModel):
    id: int
    name: str
    muscle_group: str
    equipment: Optional[str]
    difficulty: str
    description: Optional[str]

    model_config = {"from_attributes": True}
