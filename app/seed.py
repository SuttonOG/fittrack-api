"""Populate the database with a starter set of common exercises.

Run once after creating the database:
    python -m app.seed
"""

from app.database import SessionLocal, engine, Base
from app.models.exercise import Exercise

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
        existing = {e.name for e in db.query(Exercise.name).all()}
        added = 0
        for ex in EXERCISES:
            if ex["name"] not in existing:
                db.add(Exercise(**ex))
                added += 1
        db.commit()
        print(f"Seeded {added} exercises ({len(existing)} already existed).")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
