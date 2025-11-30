from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from habit_tracker.application.repositories import (
    CompletionRepository,
    HabitRepository,
    ReminderRepository,
    UserRepository,
)
from habit_tracker.domain.completion import Completion
from habit_tracker.domain.habit import Habit
from habit_tracker.domain.reminder import Reminder
from habit_tracker.domain.user import User


class InMemoryHabitRepository(HabitRepository):
    """Simple in-memory habit store using a dict."""

    def __init__(self) -> None:
        self._habits: dict[UUID, Habit] = {}

    def add(self, habit: Habit) -> None:
        self._habits[habit.id] = habit

    def get(self, habit_id: UUID) -> Habit:
        try:
            return self._habits[habit_id]
        except KeyError as exc:
            raise KeyError(f"Habit {habit_id} not found") from exc

    def get_by_user_id(self, user_id: UUID) -> Habit | None:
        for habit in self._habits.values():
            if habit.user_id == user_id:
                return habit
        return None

    def list_by_user_id(self, user_id: UUID) -> list[Habit]:
        return [habit for habit in self._habits.values() if habit.user_id == user_id]

    def list_all(self) -> list[Habit]:
        # Return a copy so callers cannot mutate internal state accidentally.
        return list(self._habits.values())

    def remove(self, habit_id: UUID) -> None:
        # Use pop with default to avoid KeyError if it does not exist.
        self._habits.pop(habit_id, None)


class InMemoryCompletionRepository(CompletionRepository):
    """Simple in-memory completion store using a list."""

    def __init__(self) -> None:
        self._completions: list[Completion] = []

    def add(self, completion: Completion) -> None:
        self._completions.append(completion)

    def list_for_habit(self, habit_id: UUID) -> list[Completion]:
        result: list[Completion] = []
        for c in self._completions:
            if c.habit_id == habit_id:
                result.append(c)
        return result

    def list_for_habit_between(
        self,
        habit_id: UUID,
        start: datetime,
        end: datetime,
    ) -> list[Completion]:
        result: list[Completion] = []
        for c in self._completions:
            if c.habit_id != habit_id:
                continue
            if start <= c.completed_at <= end:
                result.append(c)
        return result


class InMemoryReminderRepository(ReminderRepository):
    """Simple in-memory reminder store.

    We assume one reminder per habit. We store by habit_id.
    """

    def __init__(self) -> None:
        self._by_habit_id: dict[UUID, Reminder] = {}

    def add(self, reminder: Reminder) -> None:
        self._by_habit_id[reminder.habit_id] = reminder

    def get_by_habit_id(self, habit_id: UUID) -> Reminder | None:
        return self._by_habit_id.get(habit_id)

    def list_due(self, before: datetime) -> list[Reminder]:
        if before.tzinfo is None:
            before = before.replace(tzinfo=UTC)

        due: list[Reminder] = []
        for r in self._by_habit_id.values():
            if not r.active:
                continue
            if r.next_due_at <= before:
                due.append(r)
        return due


class InMemoryUserRepository(UserRepository):
    """Simple in-memory user store using a dict."""

    def __init__(self) -> None:
        self._users: dict[UUID, User] = {}

    def add(self, user: User) -> None:
        self._users[user.id] = user

    def get(self, user_id: UUID) -> User:
        try:
            return self._users[user_id]
        except KeyError as exc:
            raise KeyError(f"User {user_id} not found") from exc

    def get_by_email(self, email: str) -> User | None:
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    def list_all(self) -> list[User]:
        return list(self._users.values())

    def remove(self, user_id: UUID) -> None:
        self._users.pop(user_id, None)
