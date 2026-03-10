"""Tests for /exercises CRUD endpoints."""


def test_create_exercise(auth_client):
    resp = auth_client.post("/exercises/", json={
        "name": "Squat",
        "muscle_group": "legs",
        "difficulty": "intermediate",
    })
    assert resp.status_code == 201
    assert resp.json()["name"] == "Squat"


def test_create_duplicate_exercise(auth_client, sample_exercise):
    resp = auth_client.post("/exercises/", json={
        "name": "Barbell Bench Press",
        "muscle_group": "chest",
        "difficulty": "intermediate",
    })
    assert resp.status_code == 409


def test_list_exercises(client, sample_exercise):
    resp = client.get("/exercises/")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_list_exercises_filter_muscle_group(client, sample_exercise):
    resp = client.get("/exercises/?muscle_group=chest")
    assert resp.status_code == 200
    assert all(e["muscle_group"] == "chest" for e in resp.json())


def test_get_exercise(client, sample_exercise):
    resp = client.get(f"/exercises/{sample_exercise.id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == sample_exercise.id


def test_get_exercise_not_found(client):
    resp = client.get("/exercises/9999")
    assert resp.status_code == 404


def test_update_exercise(auth_client, sample_exercise):
    resp = auth_client.put(f"/exercises/{sample_exercise.id}", json={
        "difficulty": "advanced",
    })
    assert resp.status_code == 200
    assert resp.json()["difficulty"] == "advanced"


def test_delete_exercise(auth_client, sample_exercise):
    resp = auth_client.delete(f"/exercises/{sample_exercise.id}")
    assert resp.status_code == 204
