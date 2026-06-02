import pytest


pytestmark = pytest.mark.integration


def test_healthz_returns_ok(client):
    response = client.get("/api/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_register_login_and_get_current_user(client):
    register_response = client.post(
        "/api/auth/register",
        json={"email": "Student@Example.com", "password": "password123"},
    )

    assert register_response.status_code == 201
    register_token = register_response.json()["access_token"]

    me_response = client.get(
        "/api/users/me", headers={"Authorization": f"Bearer {register_token}"}
    )

    assert me_response.status_code == 200
    assert me_response.json()["email"] == "student@example.com"
    assert me_response.json()["role"] == "student"

    login_response = client.post(
        "/api/auth/login",
        json={"email": "student@example.com", "password": "password123"},
    )

    assert login_response.status_code == 200
    assert login_response.json()["access_token"]


def test_get_current_user_rejects_missing_token(client):
    response = client.get("/api/users/me")

    assert response.status_code == 401
