"""Exercise model — catalogue of available exercises with metadata."""

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    muscle_group = Column(String(50), nullable=False, index=True)
    equipment = Column(String(50), nullable=True)
    difficulty = Column(String(20), nullable=False, default="intermediate")
    description = Column(Text, nullable=True)

    # Relationships
    workout_logs = relationship("WorkoutLog", back_populates="exercise")
