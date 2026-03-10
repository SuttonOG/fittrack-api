"""Application configuration using environment variables with sensible defaults."""

import os


class Settings:
    """Central configuration for the FitTrack API."""

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./fittrack.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    APP_TITLE: str = "FitTrack API"
    APP_DESCRIPTION: str = (
        "A workout and fitness analytics API for tracking exercises, "
        "workout plans, logged sessions, and performance insights."
    )
    APP_VERSION: str = "1.0.0"


settings = Settings()
