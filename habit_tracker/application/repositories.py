from __future__ import annotations

from datetime import datetime
from typing import Protocol, List
from uuid import UUID

from habit_tracker.domain import Habit, Completion, Reminder


class HabitRepository(Protocol):
    """Port for storing and retrieving habits."""

    def add(self, habit: Habit) -> None:
        """Store a new habit or overwrite an existing one with the same ID."""
        ...

    def get(self, habit_id: UUID) -> Habit:
        """Return the habit with the given ID, or raise an error if not found."""
        ...

    def list_all(self) -> List[Habit]:
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

    def list_for_habit(self, habit_id: UUID) -> List[Completion]:
        """Return all completions for the given habit."""
        ...

    def list_for_habit_between(
        self,
        habit_id: UUID,
        start: datetime,
        end: datetime,
    ) -> List[Completion]:
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

    def list_due(self, before: datetime) -> List[Reminder]:
        """Return all reminders with next_due_at <= 'before' and active=True."""
        ...
