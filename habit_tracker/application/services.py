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

from .repositories import HabitRepository, CompletionRepository
from .event_bus import EventBus


@dataclass
class HabitTrackerService:
    """Application service coordinating domain objects and repositories."""

    habit_repo: HabitRepository
    completion_repo: CompletionRepository
    clock: Clock
    event_bus: EventBus | None = None

    # ------------------------------
    # Habits
    # ------------------------------

    def create_habit(self, name: str, schedule: Schedule) -> Habit:
        result = Habit.create(
            name=name,
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

    # ------------------------------
    # Completions
    # ------------------------------

    def complete_habit(self, habit_id: UUID) -> Completion:
        habit = self.habit_repo.get(habit_id)

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
        rule: StreakRule | None = None,
    ) -> Streak:
        habit = self.habit_repo.get(habit_id)
        completions = self.completion_repo.list_for_habit(habit_id)
        now = self.clock.now()

        if rule is None:
            rule = make_streak_rule(habit.schedule)

        streak = rule.calculate(habit=habit, completions=completions, now=now)
        return streak

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
