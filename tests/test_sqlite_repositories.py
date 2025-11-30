from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta

from habit_tracker.domain.completion import Completion
from habit_tracker.domain.habit import Habit
from habit_tracker.domain.reminder import Reminder
from habit_tracker.domain.schedule import Schedule
from habit_tracker.domain.user import User
from habit_tracker.infrastructure.sqlite_repositories import (
    SQLiteCompletionRepository,
    SQLiteHabitRepository,
    SQLiteReminderRepository,
    SQLiteUserRepository,
)

from tests.utils import FakeClock


def _make_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    return conn


def _create_habit(
    clock: FakeClock, habit_repo: SQLiteHabitRepository, user_repo: SQLiteUserRepository
) -> Habit:
    # Create user first to satisfy foreign key constraint
    user = User.create(
        email="test@example.com",
        hashed_password="hashed",
        clock=clock,
    )
    user_repo.add(user)

    result = Habit.create(
        name="Test habit",
        user_id=user.id,
        schedule=Schedule("daily"),
        clock=clock,
    )
    if isinstance(result, tuple):
        habit, _event = result
    else:
        habit = result
    habit_repo.add(habit)
    return habit


def _record_completion(habit: Habit, clock: FakeClock) -> Completion:
    result = Completion.record(habit=habit, clock=clock)
    if isinstance(result, tuple):
        completion, _event = result
    else:
        completion = result
    return completion


def test_sqlite_habit_repository_roundtrip() -> None:
    conn = _make_connection()
    habit_repo = SQLiteHabitRepository(conn)
    user_repo = SQLiteUserRepository(conn)
    clock = FakeClock(datetime(2025, 1, 1, 9, 0, 0))

    habit = _create_habit(clock, habit_repo, user_repo)

    loaded = habit_repo.get(habit.id)
    assert loaded == habit

    all_habits = habit_repo.list_all()
    assert habit in all_habits

    habit_repo.remove(habit.id)
    all_after_remove = habit_repo.list_all()
    assert habit not in all_after_remove


def test_sqlite_completion_repository_roundtrip() -> None:
    conn = _make_connection()
    habit_repo = SQLiteHabitRepository(conn)
    user_repo = SQLiteUserRepository(conn)
    completion_repo = SQLiteCompletionRepository(conn)
    clock = FakeClock(datetime(2025, 1, 1, 9, 0, 0))

    habit = _create_habit(clock, habit_repo, user_repo)

    # Two completions on different days
    c1 = _record_completion(habit, clock)
    completion_repo.add(c1)

    clock.set(clock.now() + timedelta(days=1))
    c2 = _record_completion(habit, clock)
    completion_repo.add(c2)

    all_for_habit = completion_repo.list_for_habit(habit.id)
    assert len(all_for_habit) == 2

    between = completion_repo.list_for_habit_between(
        habit_id=habit.id,
        start=c1.completed_at,
        end=c1.completed_at,
    )
    assert [c.completed_at for c in between] == [c1.completed_at]


def test_sqlite_reminder_repository_roundtrip() -> None:
    conn = _make_connection()
    reminder_repo = SQLiteReminderRepository(conn)
    habit_repo = SQLiteHabitRepository(conn)
    user_repo = SQLiteUserRepository(conn)
    clock = FakeClock(datetime(2025, 1, 1, 9, 0, 0))

    # Create user first
    user = User.create(
        email="test@example.com",
        hashed_password="hashed",
        clock=clock,
    )
    user_repo.add(user)

    habit_id = Habit.create(
        name="Temp",
        user_id=user.id,
        schedule=Schedule("daily"),
        clock=clock,
    )
    # Habit.create may return (habit, event)
    if isinstance(habit_id, tuple):
        habit, _ = habit_id
    else:
        habit = habit_id

    habit_repo.add(habit)

    reminder = Reminder(
        id=habit.id,  # simplification: same UUID
        habit_id=habit.id,
        next_due_at=datetime(2025, 1, 2, 9, 0, 0),
        active=True,
    )

    reminder_repo.add(reminder)
    loaded = reminder_repo.get_by_habit_id(habit.id)

    assert loaded is not None
    assert loaded.habit_id == reminder.habit_id
    assert loaded.next_due_at == reminder.next_due_at
    assert loaded.active is True

    # Due query
    due = reminder_repo.list_due(datetime(2025, 1, 3, 0, 0, 0))
    assert any(r.habit_id == habit.id for r in due)


def test_sqlite_user_repository_roundtrip() -> None:
    conn = _make_connection()
    user_repo = SQLiteUserRepository(conn)
    clock = FakeClock(datetime(2025, 1, 1, 9, 0, 0))

    user = User.create(
        email="test@example.com",
        hashed_password="password",
        clock=clock,
    )
    user_repo.add(user)

    loaded = user_repo.get(user.id)
    assert loaded == user

    all_users = user_repo.list_all()
    assert user in all_users

    user_repo.remove(user.id)
    all_after_remove = user_repo.list_all()
    assert user not in all_after_remove
