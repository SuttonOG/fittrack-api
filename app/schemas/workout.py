"""Pydantic schemas for workout plan CRUD operations."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class WorkoutCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["Push Day A"])
    description: Optional[str] = Field(None, examples=["Heavy chest and triceps"])
    scheduled_date: Optional[str] = Field(None, examples=["2026-03-15"])


class WorkoutUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    scheduled_date: Optional[str] = None


class WorkoutRead(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str]
    scheduled_date: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
