from __future__ import annotations

from fastapi.testclient import TestClient
from habit_tracker.interfaces.api.app import create_app


def _make_client() -> TestClient:
    app = create_app()
    return TestClient(app)


def _register_and_login(client: TestClient, email: str, password: str) -> str:
    """Register a user and return their access token."""
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


def test_users_see_only_their_own_habits() -> None:
    """Test that User A and User B each see only their own habits."""
    client = _make_client()

    # Register and login user A
    token_a = _register_and_login(client, "user_a@example.com", "password_a")

    # Register and login user B
    token_b = _register_and_login(client, "user_b@example.com", "password_b")

    # User A creates 2 habits
    resp_a1 = client.post(
        "/habits",
        json={"name": "Exercise A1", "schedule": "daily"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert resp_a1.status_code == 201
    habit_a1_id = resp_a1.json()["id"]

    resp_a2 = client.post(
        "/habits",
        json={"name": "Exercise A2", "schedule": "daily"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert resp_a2.status_code == 201
    habit_a2_id = resp_a2.json()["id"]

    # User B creates 1 habit
    resp_b1 = client.post(
        "/habits",
        json={"name": "Exercise B1", "schedule": "daily"},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert resp_b1.status_code == 201
    habit_b1_id = resp_b1.json()["id"]

    # User A lists habits - should only see their 2 habits
    resp_list_a = client.get(
        "/habits",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert resp_list_a.status_code == 200
    habits_a = resp_list_a.json()
    assert len(habits_a) == 2
    habit_ids_a = {h["id"] for h in habits_a}
    assert habit_a1_id in habit_ids_a
    assert habit_a2_id in habit_ids_a
    assert habit_b1_id not in habit_ids_a

    # User B lists habits - should only see their 1 habit
    resp_list_b = client.get(
        "/habits",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert resp_list_b.status_code == 200
    habits_b = resp_list_b.json()
    assert len(habits_b) == 1
    assert habits_b[0]["id"] == habit_b1_id
    assert habits_b[0]["name"] == "Exercise B1"


def test_user_cannot_complete_another_users_habit() -> None:
    """Test that User B cannot complete User A's habit."""
    client = _make_client()

    # Register and login user A
    token_a = _register_and_login(client, "user_a2@example.com", "password_a")

    # Register and login user B
    token_b = _register_and_login(client, "user_b2@example.com", "password_b")

    # User A creates a habit
    resp_a = client.post(
        "/habits",
        json={"name": "Exercise A", "schedule": "daily"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert resp_a.status_code == 201
    habit_a_id = resp_a.json()["id"]

    # User B tries to complete User A's habit - should get 404
    resp_complete = client.post(
        f"/habits/{habit_a_id}/complete",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert resp_complete.status_code == 404
    assert "not found" in resp_complete.json()["detail"].lower()

    # User A can complete their own habit
    resp_complete_a = client.post(
        f"/habits/{habit_a_id}/complete",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert resp_complete_a.status_code == 200
