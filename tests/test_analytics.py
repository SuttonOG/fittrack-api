"""Tests for /analytics endpoints."""

import pytest


@pytest.fixture
def seeded_logs(auth_client, sample_exercise):
    """Create a workout with several log entries for analytics testing."""
    w = auth_client.post("/workouts/", json={"name": "Analytics Test"}).json()
    wid = w["id"]
    eid = sample_exercise.id

    # Log a few entries with varying weights
    for weight in [60.0, 80.0, 100.0, 90.0]:
        auth_client.post("/logs/", json={
            "workout_id": wid,
            "exercise_id": eid,
            "sets": 4,
            "reps": 8,
            "weight_kg": weight,
        })
    return wid, eid


def test_personal_records(auth_client, seeded_logs):
    resp = auth_client.get("/analytics/personal-records")
    assert resp.status_code == 200
    records = resp.json()["personal_records"]
    assert len(records) >= 1
    # Best weight should be 100 kg
    assert records[0]["best_weight_kg"] == 100.0


def test_volume_trends_weekly(auth_client, seeded_logs):
    resp = auth_client.get("/analytics/volume-trends?period=weekly")
    assert resp.status_code == 200
    data = resp.json()
    assert data["period"] == "weekly"
    assert len(data["trends"]) >= 1


def test_volume_trends_monthly(auth_client, seeded_logs):
    resp = auth_client.get("/analytics/volume-trends?period=monthly")
    assert resp.status_code == 200
    assert resp.json()["period"] == "monthly"


def test_muscle_group_distribution(auth_client, seeded_logs):
    resp = auth_client.get("/analytics/muscle-group-distribution")
    assert resp.status_code == 200
    dist = resp.json()["distribution"]
    assert len(dist) >= 1
    assert dist[0]["muscle_group"] == "chest"


def test_streak(auth_client, seeded_logs):
    resp = auth_client.get("/analytics/streak")
    assert resp.status_code == 200
    data = resp.json()
    assert "current_streak_days" in data
    assert "longest_streak_days" in data
    assert data["total_workout_days"] >= 1


def test_analytics_unauthenticated(client):
    """All analytics endpoints require authentication."""
    for path in [
        "/analytics/personal-records",
        "/analytics/volume-trends",
        "/analytics/muscle-group-distribution",
        "/analytics/streak",
    ]:
        assert client.get(path).status_code == 401
