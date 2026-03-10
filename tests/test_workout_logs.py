"""Tests for /logs CRUD endpoints."""

import pytest


@pytest.fixture
def workout_and_exercise(auth_client, sample_exercise):
    """Create a workout and return (workout_id, exercise_id)."""
    resp = auth_client.post("/workouts/", json={"name": "Test Workout"})
    return resp.json()["id"], sample_exercise.id


def test_create_log(auth_client, workout_and_exercise):
    wid, eid = workout_and_exercise
    resp = auth_client.post("/logs/", json={
        "workout_id": wid,
        "exercise_id": eid,
        "sets": 4,
        "reps": 10,
        "weight_kg": 80.0,
    })
    assert resp.status_code == 201
    assert resp.json()["sets"] == 4


def test_create_log_nonexistent_exercise(auth_client, workout_and_exercise):
    wid, _ = workout_and_exercise
    resp = auth_client.post("/logs/", json={
        "workout_id": wid,
        "exercise_id": 9999,
        "sets": 3,
        "reps": 8,
    })
    assert resp.status_code == 404


def test_list_logs(auth_client, workout_and_exercise):
    wid, eid = workout_and_exercise
    auth_client.post("/logs/", json={"workout_id": wid, "exercise_id": eid, "sets": 3, "reps": 10})
    auth_client.post("/logs/", json={"workout_id": wid, "exercise_id": eid, "sets": 4, "reps": 8})
    resp = auth_client.get("/logs/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_update_log(auth_client, workout_and_exercise):
    wid, eid = workout_and_exercise
    create = auth_client.post("/logs/", json={
        "workout_id": wid, "exercise_id": eid, "sets": 3, "reps": 10,
    })
    log_id = create.json()["id"]
    resp = auth_client.put(f"/logs/{log_id}", json={"sets": 5})
    assert resp.status_code == 200
    assert resp.json()["sets"] == 5


def test_delete_log(auth_client, workout_and_exercise):
    wid, eid = workout_and_exercise
    create = auth_client.post("/logs/", json={
        "workout_id": wid, "exercise_id": eid, "sets": 3, "reps": 10,
    })
    log_id = create.json()["id"]
    resp = auth_client.delete(f"/logs/{log_id}")
    assert resp.status_code == 204
