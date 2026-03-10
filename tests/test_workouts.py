"""Tests for /workouts CRUD endpoints."""


def test_create_workout(auth_client):
    resp = auth_client.post("/workouts/", json={
        "name": "Push Day",
        "description": "Chest and triceps",
        "scheduled_date": "2026-03-20",
    })
    assert resp.status_code == 201
    assert resp.json()["name"] == "Push Day"


def test_list_workouts_empty(auth_client):
    resp = auth_client.get("/workouts/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_workouts(auth_client):
    auth_client.post("/workouts/", json={"name": "Day A"})
    auth_client.post("/workouts/", json={"name": "Day B"})
    resp = auth_client.get("/workouts/")
    assert len(resp.json()) == 2


def test_get_workout(auth_client):
    create_resp = auth_client.post("/workouts/", json={"name": "Leg Day"})
    wid = create_resp.json()["id"]
    resp = auth_client.get(f"/workouts/{wid}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Leg Day"


def test_update_workout(auth_client):
    create_resp = auth_client.post("/workouts/", json={"name": "Old Name"})
    wid = create_resp.json()["id"]
    resp = auth_client.put(f"/workouts/{wid}", json={"name": "New Name"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "New Name"


def test_delete_workout(auth_client):
    create_resp = auth_client.post("/workouts/", json={"name": "To Delete"})
    wid = create_resp.json()["id"]
    resp = auth_client.delete(f"/workouts/{wid}")
    assert resp.status_code == 204


def test_get_other_users_workout(auth_client, client):
    """Ensure a user cannot access another user's workout."""
    create_resp = auth_client.post("/workouts/", json={"name": "Private"})
    wid = create_resp.json()["id"]

    # Register + login as a different user
    client.post("/auth/register", json={
        "username": "other", "email": "other@example.com", "password": "pass123"
    })
    login = client.post("/auth/login", json={"username": "other", "password": "pass123"})
    other_token = login.json()["access_token"]

    resp = client.get(f"/workouts/{wid}", headers={"Authorization": f"Bearer {other_token}"})
    assert resp.status_code == 404
