"""Tests for /auth endpoints: register, login, and /me."""


def test_register_success(client):
    resp = client.post("/auth/register", json={
        "username": "newuser",
        "email": "new@example.com",
        "password": "securepass",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "newuser"
    assert "id" in data


def test_register_duplicate_username(client, test_user):
    resp = client.post("/auth/register", json={
        "username": "testuser",
        "email": "other@example.com",
        "password": "securepass",
    })
    assert resp.status_code == 409


def test_login_success(client, test_user):
    resp = client.post("/auth/login", json={
        "username": "testuser",
        "password": "password123",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client, test_user):
    resp = client.post("/auth/login", json={
        "username": "testuser",
        "password": "wrongpass",
    })
    assert resp.status_code == 401


def test_me_authenticated(auth_client):
    resp = auth_client.get("/auth/me")
    assert resp.status_code == 200
    assert resp.json()["username"] == "testuser"


def test_me_unauthenticated(client):
    resp = client.get("/auth/me")
    assert resp.status_code == 401
