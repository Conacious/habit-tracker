from fastapi.testclient import TestClient
from habit_tracker.infrastructure.settings import get_settings
from habit_tracker.interfaces.api.app import create_app


def _make_client() -> TestClient:
    get_settings.cache_clear()
    app = create_app()
    return TestClient(app)


def test_login_returns_token() -> None:
    client = _make_client()

    # register first
    reg = client.post(
        "/auth/register",
        json={"email": "login@example.com", "password": "secret123"},
    )
    assert reg.status_code == 201

    # login
    resp = client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "secret123"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_with_wrong_password() -> None:
    client = _make_client()

    # register user first
    reg = client.post(
        "/auth/register",
        json={"email": "wrong-login@example.com", "password": "secret1234"},
    )

    assert reg.status_code == 201

    resp = client.post(
        "/auth/login",
        json={"email": "wrong-login@example.com", "password": "wrongpassword"},
    )
    assert resp.status_code == 401


def test_me_endpoint_requires_token() -> None:
    client = _make_client()

    # call /me endpoint without token
    resp = client.get("/me")

    assert resp.status_code == 401

    # register first
    reg = client.post(
        "/auth/register",
        json={"email": "me@example.com", "password": "secret1234"},
    )

    assert reg.status_code == 201

    # login
    token_resp = client.post(
        "/auth/login",
        json={"email": "me@example.com", "password": "secret1234"},
    )

    assert token_resp.status_code == 200

    token = token_resp.json()["access_token"]

    # call /me endpoint with token
    resp = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert "email" in data
    assert data["email"] == "me@example.com"
