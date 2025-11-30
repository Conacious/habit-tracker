from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from habit_tracker.domain.clock import Clock
from habit_tracker.domain.habit import Habit
from habit_tracker.domain.completion import Completion
from habit_tracker.domain.schedule import Schedule
from habit_tracker.domain.streak import Streak
from habit_tracker.domain.streak_rules import StreakRule
from habit_tracker.domain.streak_factory import make_streak_rule
from habit_tracker.domain.events import DomainEvent
from habit_tracker.domain.user import User
from habit_tracker.application.security import hash_password, verify_password

from .repositories import (
    HabitRepository,
    CompletionRepository,
    ReminderRepository,
    UserRepository,
)
from .event_bus import EventBus


@dataclass
class HabitTrackerService:
    """Application service coordinating domain objects and repositories."""

    habit_repo: HabitRepository
    completion_repo: CompletionRepository
    clock: Clock
    reminder_repo: ReminderRepository | None = None
    event_bus: EventBus | None = None

    # ------------------------------
    # Habits
    # ------------------------------

    def create_habit(self, name: str, schedule: Schedule, user_id: UUID) -> Habit:
        result = Habit.create(
            name=name,
            user_id=user_id,
            schedule=schedule,
            clock=self.clock,
        )

        if isinstance(result, tuple):
            habit, event = result
        else:
            habit, event = result, None

        self.habit_repo.add(habit)
        self._publish(event)
        return habit

    def list_habits(self) -> list[Habit]:
        return self.habit_repo.list_all()

    def list_habits_for_user(self, user_id: UUID) -> list[Habit]:
        return self.habit_repo.list_by_user_id(user_id)

    # ------------------------------
    # Completions
    # ------------------------------

    def complete_habit(self, habit_id: UUID, user_id: UUID) -> Completion:
        habit = self.habit_repo.get(habit_id)

        if habit.user_id != user_id:
            raise PermissionError("Habit does not belong to user")

        result = Completion.record(
            habit=habit,
            clock=self.clock,
        )

        if isinstance(result, tuple):
            completion, event = result
        else:
            completion, event = result, None

        self.completion_repo.add(completion)
        self._publish(event)
        return completion

    # ------------------------------
    # Streaks
    # ------------------------------

    def calculate_streak(
        self,
        habit_id: UUID,
        user_id: UUID,
        rule: StreakRule | None = None,
    ) -> Streak:
        habit = self.habit_repo.get(habit_id)

        if habit.user_id != user_id:
            raise PermissionError("Habit does not belong to user")

        completions = self.completion_repo.list_for_habit(habit_id)
        now = self.clock.now()

        if rule is None:
            rule = make_streak_rule(habit.schedule)

        streak = rule.calculate(habit=habit, completions=completions, now=now)
        return streak

    # ------------------------------
    # Reminders
    # ------------------------------

    def get_reminder(self, habit_id: UUID) -> Reminder | None:
        if self.reminder_repo is None:
            return None

        return self.reminder_repo.get_by_habit_id(habit_id)

    def list_due_reminders(
        self, before: datetime | None = None
    ) -> list[Reminder] | None:
        if self.reminder_repo is None:
            return None

        return self.reminder_repo.list_due(before=before)

    # ------------------------------
    # Internal helpers
    # ------------------------------

    def _publish(self, event: DomainEvent | None) -> None:
        """Publish an event if we have an event bus configured."""
        if event is None:
            return
        if self.event_bus is None:
            return
        self.event_bus.publish(event)


class EmailAlreadyRegisteredError(Exception):
    pass


@dataclass
class UserRegistrationService:
    user_repo: UserRepository
    clock: Clock

    def register_user(self, email: str, password: str) -> User:
        existing = self.user_repo.get_by_email(email)
        if existing is not None:
            raise EmailAlreadyRegisteredError(f"Email already registered: {email}")

        # TODO: you can add some simple validation:
        # if len(password) < 8: raise ValueError("Password too short")

        hashed = hash_password(password)
        user = User.create(email=email, hashed_password=hashed, clock=self.clock)
        self.user_repo.add(user)
        return user

    def list_users(self) -> list[User]:
        return self.user_repo.list_all()


@dataclass
class AuthenticationService:
    user_repo: UserRepository

    def authenticate(self, email: str, password: str) -> User | None:
        user = self.user_repo.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            return None
        return user
