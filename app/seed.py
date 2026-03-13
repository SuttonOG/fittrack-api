"""Populate the database with starter exercises and strength benchmark data.

Run once after creating the database:
    python -m app.seed
"""

import csv
from pathlib import Path

from app.database import SessionLocal, engine, Base
from app.models.exercise import Exercise
from app.models.benchmark import Benchmark

EXERCISES = [
    {"name": "Barbell Bench Press", "muscle_group": "chest", "equipment": "barbell", "difficulty": "intermediate", "description": "Flat bench press targeting the pectorals."},
    {"name": "Incline Dumbbell Press", "muscle_group": "chest", "equipment": "dumbbells", "difficulty": "intermediate", "description": "Incline press emphasising the upper chest."},
    {"name": "Barbell Back Squat", "muscle_group": "legs", "equipment": "barbell", "difficulty": "intermediate", "description": "Compound lower-body movement."},
    {"name": "Romanian Deadlift", "muscle_group": "legs", "equipment": "barbell", "difficulty": "intermediate", "description": "Hip-hinge movement targeting hamstrings and glutes."},
    {"name": "Leg Press", "muscle_group": "legs", "equipment": "machine", "difficulty": "beginner", "description": "Machine-based quad-dominant press."},
    {"name": "Pull-Up", "muscle_group": "back", "equipment": "bodyweight", "difficulty": "intermediate", "description": "Vertical pulling movement for lats."},
    {"name": "Barbell Row", "muscle_group": "back", "equipment": "barbell", "difficulty": "intermediate", "description": "Horizontal row targeting the upper back."},
    {"name": "Overhead Press", "muscle_group": "shoulders", "equipment": "barbell", "difficulty": "intermediate", "description": "Standing press for anterior deltoids."},
    {"name": "Lateral Raise", "muscle_group": "shoulders", "equipment": "dumbbells", "difficulty": "beginner", "description": "Isolation movement for lateral deltoids."},
    {"name": "Barbell Curl", "muscle_group": "arms", "equipment": "barbell", "difficulty": "beginner", "description": "Bicep curl with a straight bar."},
    {"name": "Tricep Dip", "muscle_group": "arms", "equipment": "bodyweight", "difficulty": "intermediate", "description": "Bodyweight pressing for triceps."},
    {"name": "Plank", "muscle_group": "core", "equipment": "bodyweight", "difficulty": "beginner", "description": "Isometric core hold."},
    {"name": "Cable Crunch", "muscle_group": "core", "equipment": "cable", "difficulty": "beginner", "description": "Weighted abdominal crunch using cable machine."},
    {"name": "Deadlift", "muscle_group": "back", "equipment": "barbell", "difficulty": "advanced", "description": "Full-body posterior chain compound lift."},
    {"name": "Dumbbell Lunge", "muscle_group": "legs", "equipment": "dumbbells", "difficulty": "beginner", "description": "Unilateral leg movement for quads and glutes."},
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # ── Seed exercises ────────────────────────────
        existing = {e.name for e in db.query(Exercise.name).all()}
        added = 0
        for ex in EXERCISES:
            if ex["name"] not in existing:
                db.add(Exercise(**ex))
                added += 1
        db.commit()
        print(f"Seeded {added} exercises ({len(existing)} already existed).")

        # ── Seed benchmarks from CSV ─────────────────
        csv_path = Path(__file__).parent.parent / "data" / "strength_benchmarks.csv"
        if not csv_path.exists():
            print(f"Benchmark CSV not found at {csv_path}, skipping.")
            return

        existing_benchmarks = db.query(Benchmark).count()
        if existing_benchmarks > 0:
            print(f"Benchmarks already seeded ({existing_benchmarks} rows), skipping.")
            return

        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f)
            bench_count = 0
            for row in reader:
                db.add(Benchmark(
                    exercise_name=row["exercise_name"],
                    gender=row["gender"],
                    bodyweight_kg=float(row["bodyweight_kg"]),
                    beginner_kg=float(row["beginner_kg"]),
                    novice_kg=float(row["novice_kg"]),
                    intermediate_kg=float(row["intermediate_kg"]),
                    advanced_kg=float(row["advanced_kg"]),
                    elite_kg=float(row["elite_kg"]),
                ))
                bench_count += 1
        db.commit()
        print(f"Seeded {bench_count} benchmark rows from CSV.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()