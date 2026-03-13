"""Tests for /analytics/benchmarks endpoint."""

import pytest
from app.models.benchmark import Benchmark


@pytest.fixture
def seeded_benchmarks(db_session):
    """Insert benchmark data for testing."""
    benchmarks = [
        Benchmark(exercise_name="Barbell Bench Press", gender="male", bodyweight_kg=80,
                   beginner_kg=40, novice_kg=60, intermediate_kg=85, advanced_kg=110, elite_kg=140),
        Benchmark(exercise_name="Barbell Bench Press", gender="female", bodyweight_kg=60,
                   beginner_kg=15, novice_kg=25, intermediate_kg=40, advanced_kg=55, elite_kg=75),
    ]
    for b in benchmarks:
        db_session.add(b)
    db_session.commit()
    return benchmarks


@pytest.fixture
def logs_with_bench_press(auth_client, sample_exercise):
    """Create a workout and log a bench press entry."""
    w = auth_client.post("/workouts/", json={"name": "Bench Test"}).json()
    auth_client.post("/logs/", json={
        "workout_id": w["id"],
        "exercise_id": sample_exercise.id,
        "sets": 3,
        "reps": 5,
        "weight_kg": 90.0,
    })
    return w["id"]


def test_benchmarks_returns_comparison(auth_client, seeded_benchmarks, logs_with_bench_press):
    resp = auth_client.get("/analytics/benchmarks?gender=male&bodyweight_kg=80")
    assert resp.status_code == 200
    data = resp.json()
    assert data["gender"] == "male"
    assert data["bodyweight_kg"] == 80
    assert len(data["comparisons"]) >= 1
    comp = data["comparisons"][0]
    assert comp["exercise_name"] == "Barbell Bench Press"
    assert comp["your_pr_kg"] == 90.0
    assert comp["classification"] == "intermediate"
    assert "estimated_percentile" in comp
    assert "standards" in comp


def test_benchmarks_no_logs(auth_client, seeded_benchmarks):
    resp = auth_client.get("/analytics/benchmarks?gender=male&bodyweight_kg=80")
    assert resp.status_code == 200
    assert resp.json()["comparisons"] == []


def test_benchmarks_female(auth_client, seeded_benchmarks, logs_with_bench_press):
    resp = auth_client.get("/analytics/benchmarks?gender=female&bodyweight_kg=60")
    assert resp.status_code == 200
    comp = resp.json()["comparisons"][0]
    assert comp["classification"] == "elite"


def test_benchmarks_invalid_gender(auth_client):
    resp = auth_client.get("/analytics/benchmarks?gender=other&bodyweight_kg=80")
    assert resp.status_code == 422


def test_benchmarks_missing_params(auth_client):
    resp = auth_client.get("/analytics/benchmarks")
    assert resp.status_code == 422


def test_benchmarks_unauthenticated(client):
    resp = client.get("/analytics/benchmarks?gender=male&bodyweight_kg=80")
    assert resp.status_code == 401