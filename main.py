"""FitTrack API — Workout & Fitness Analytics.

Entry point that wires together all routers and creates the database tables
on startup.  Run with:
    uvicorn main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.database import engine, Base
from app.routers import auth, exercises, workouts, workout_logs, analytics


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup (safe to call repeatedly)."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Register routers
app.include_router(auth.router)
app.include_router(exercises.router)
app.include_router(workouts.router)
app.include_router(workout_logs.router)
app.include_router(analytics.router)


@app.get("/", tags=["Root"])
def root():
    """Health-check / welcome endpoint."""
    return {
        "message": "Welcome to the FitTrack API",
        "docs": "/docs",
        "version": settings.APP_VERSION,
    }
