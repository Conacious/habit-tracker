from __future__ import annotations

from uuid import UUID

from fastapi.testclient import TestClient

from habit_tracker.interfaces.api.app import create_app
import os

# Use inmemory database for tests, avoid using sqlite3 in API tests
os.environ["DATABASE_MODE"] = "inmemory"


def _make_client() -> TestClient:
    app = create_app()
    return TestClient(app)


def test_create_and_list_habits_via_api() -> None:
    client = _make_client()

    # Create habit
    resp = client.post(
        "/habits",
        json={"name": "Read", "schedule": "daily"},
    )
    assert resp.status_code == 201
    data = resp.json()
    habit_id = UUID(data["id"])
    assert data["name"] == "Read"
    assert data["schedule"] == "daily"

    # List habits
    resp_list = client.get("/habits")
    assert resp_list.status_code == 200
    habits = resp_list.json()
    assert len(habits) == 1
    assert habits[0]["id"] == str(habit_id)


def test_complete_and_get_streak_via_api() -> None:
    client = _make_client()

    # Create habit
    resp = client.post(
        "/habits",
        json={"name": "Exercise", "schedule": "daily"},
    )
    assert resp.status_code == 201
    habit_id = resp.json()["id"]

    # Complete habit
    resp_complete = client.post(f"/habits/{habit_id}/complete")
    assert resp_complete.status_code == 200
    completion = resp_complete.json()
    assert completion["habit_id"] == habit_id

    # Get streak
    resp_streak = client.get(f"/habits/{habit_id}/streak")
    assert resp_streak.status_code == 200
    streak = resp_streak.json()
    assert streak["habit_id"] == habit_id
    assert streak["count"] == 1


def test_auth_register_via_api() -> None:
    client = _make_client()

    # Register user
    resp = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "password"},
    )
    assert resp.status_code == 201
    data = resp.json()
    user_id = UUID(data["id"])
    assert data["email"] == "test@example.com"
    assert data["is_active"] is True

    # List users
    resp_list = client.get("/users")
    assert resp_list.status_code == 200
    users = resp_list.json()
    assert len(users) == 1
    assert users[0]["id"] == str(user_id)


def test_register_user_duplicate_email_fails() -> None:
    client = _make_client()

    payload = {"email": "dup@example.com", "password": "secret123"}

    resp1 = client.post("/auth/register", json=payload)
    assert resp1.status_code == 201

    resp2 = client.post("/auth/register", json=payload)
    assert resp2.status_code == 400
    assert resp2.json()["detail"] == "Email already registered"
