"""Benchmark model — population strength standards per exercise, gender, and bodyweight."""

from sqlalchemy import Column, Integer, Float, String

from app.database import Base


class Benchmark(Base):
    __tablename__ = "benchmarks"

    id = Column(Integer, primary_key=True, index=True)
    exercise_name = Column(String(100), nullable=False, index=True)
    gender = Column(String(10), nullable=False)
    bodyweight_kg = Column(Float, nullable=False)
    beginner_kg = Column(Float, nullable=False)
    novice_kg = Column(Float, nullable=False)
    intermediate_kg = Column(Float, nullable=False)
    advanced_kg = Column(Float, nullable=False)
    elite_kg = Column(Float, nullable=False)