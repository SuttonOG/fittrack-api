"""Shared pytest fixtures: in-memory SQLite database and test client."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.auth.jwt import hash_password
from app.models.user import User
from app.models.exercise import Exercise
from main import app

# In-memory SQLite for speed and isolation
TEST_DB_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """Create all tables before each test; drop them after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Unauthenticated test client."""
    return TestClient(app)


@pytest.fixture
def db_session():
    """Raw DB session for seeding test data."""
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_user(db_session):
    """Create and return a test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("password123"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_client(client, test_user):
    """Test client with a valid JWT Authorization header."""
    resp = client.post("/auth/login", json={"username": "testuser", "password": "password123"})
    token = resp.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


@pytest.fixture
def sample_exercise(db_session):
    """Insert a sample exercise and return it."""
    ex = Exercise(
        name="Barbell Bench Press",
        muscle_group="chest",
        equipment="barbell",
        difficulty="intermediate",
        description="Flat bench press.",
    )
    db_session.add(ex)
    db_session.commit()
    db_session.refresh(ex)
    return ex
