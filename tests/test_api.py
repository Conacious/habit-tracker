from __future__ import annotations

from uuid import UUID

from fastapi.testclient import TestClient

from habit_tracker.interfaces.api.app import create_app


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
