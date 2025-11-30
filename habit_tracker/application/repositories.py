from __future__ import annotations

from datetime import datetime
from typing import Protocol
from uuid import UUID

from habit_tracker.domain import Completion, Habit, Reminder, User


class HabitRepository(Protocol):
    """Port for storing and retrieving habits."""

    def add(self, habit: Habit) -> None:
        """Store a new habit or overwrite an existing one with the same ID."""
        ...

    def get(self, habit_id: UUID) -> Habit:
        """Return the habit with the given ID, or raise an error if not found."""
        ...

    def get_by_user_id(self, user_id: UUID) -> Habit | None:
        """Return the habit with the given user ID, or None if not found."""
        ...

    def list_by_user_id(self, user_id: UUID) -> list[Habit]:
        """Return all habits for the given user."""
        ...

    def list_all(self) -> list[Habit]:
        """Return all habits."""
        ...

    def remove(self, habit_id: UUID) -> None:
        """Remove a habit (no-op if it doesn't exist)."""
        ...


class CompletionRepository(Protocol):
    """Port for storing and retrieving completions."""

    def add(self, completion: Completion) -> None:
        """Store a new completion."""
        ...

    def list_for_habit(self, habit_id: UUID) -> list[Completion]:
        """Return all completions for the given habit."""
        ...

    def list_for_habit_between(
        self,
        habit_id: UUID,
        start: datetime,
        end: datetime,
    ) -> list[Completion]:
        """Return completions for a habit between start and end, inclusive."""
        ...


class ReminderRepository(Protocol):
    """Port for storing and retrieving reminders."""

    def add(self, reminder: Reminder) -> None:
        """Store a new reminder or overwrite existing one for the same habit."""
        ...

    def get_by_habit_id(self, habit_id: UUID) -> Reminder | None:
        """Return the reminder for this habit, or None if not found."""
        ...

    def list_due(self, before: datetime) -> list[Reminder]:
        """Return all reminders with next_due_at <= 'before' and active=True."""
        ...


class UserRepository(Protocol):
    """Port for storing and retrieving users."""

    def add(self, user: User) -> None:
        """Store a new user or overwrite an existing one with the same ID."""
        ...

    def get(self, user_id: UUID) -> User:
        """Return the user with the given ID, or raise an error if not found."""
        ...

    def get_by_email(self, email: str) -> User | None:
        """Return the user with the given email, or None if not found."""
        ...

    def list_all(self) -> list[User]:
        """Return all users."""
        ...

    def remove(self, user_id: UUID) -> None:
        """Remove a user (no-op if it doesn't exist)."""
        ...
