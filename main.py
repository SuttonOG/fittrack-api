"""FitTrack API — Workout & Fitness Analytics.

Entry point that wires together all routers and creates the database tables
on startup.  Run with:
    uvicorn main:app --reload
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

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

# CORS — allow the frontend (and any local dev tools) to reach the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(exercises.router)
app.include_router(workouts.router)
app.include_router(workout_logs.router)
app.include_router(analytics.router)

# Serve the frontend dashboard
STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", tags=["Root"])
def root():
    """Serve the FitTrack dashboard (or JSON health-check via Accept header)."""
    index = STATIC_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {
        "message": "Welcome to the FitTrack API",
        "docs": "/docs",
        "version": settings.APP_VERSION,
    }
