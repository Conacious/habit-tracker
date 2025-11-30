from __future__ import annotations

from uuid import UUID

from fastapi.testclient import TestClient
from habit_tracker.interfaces.api.app import create_app


def _make_client() -> TestClient:
    app = create_app()
    return TestClient(app)


def _get_auth_token(
    client: TestClient, email: str = "test@example.com", password: str = "password"
) -> str:
    """Register and login a user, return the access token."""
    # Register
    client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    # Login
    resp = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    return resp.json()["access_token"]


def test_get_habit_reminder() -> None:
    client = _make_client()
    token = _get_auth_token(client)

    # Create a daily habit
    resp = client.post(
        "/habits",
        json={"name": "Drink water", "schedule": "daily"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    habit = resp.json()
    habit_id = habit["id"]

    # Reminder should be auto-created by the event handler
    resp_rem = client.get(f"/habits/{habit_id}/reminder")
    assert resp_rem.status_code == 200
    data = resp_rem.json()

    assert UUID(data["id"])  # valid UUID
    assert data["habit_id"] == habit_id
    assert data["active"] is True


def test_list_due_reminders() -> None:
    client = _make_client()
    token = _get_auth_token(client)

    # Create two habits
    for name in ["Read", "Exercise"]:
        resp = client.post(
            "/habits",
            json={"name": name, "schedule": "daily"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201

    # Ask for reminders due before a far-future date
    resp = client.get("/reminders/due", params={"before": "2100-01-01T00:00:00"})
    assert resp.status_code == 200

    reminders = resp.json()
    # At least these 2 reminders should be considered "due" by that far future
    assert len(reminders) >= 2
