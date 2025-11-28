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

from .repositories import HabitRepository, CompletionRepository


@dataclass
class HabitTrackerService:
    """Application service coordinating domain objects and repositories.

    Important: this layer does NOT know whether storage is in-memory, SQLite, etc.
    It only talks to the repository interfaces (ports).
    """

    habit_repo: HabitRepository
    completion_repo: CompletionRepository
    clock: Clock

    # ------------------------------
    # Habits
    # ------------------------------

    def create_habit(self, name: str, schedule: Schedule) -> Habit:
        """Create and store a new habit, returning the Habit entity.

        Domain events are returned by Habit.create, but we ignore them for now.
        We'll hook an event bus later.
        """
        # Depending on your implementation, Habit.create might return:
        # - (habit, event) or just habit. We assume (habit, event) from your homework.
        habit, _event = Habit.create(
            name=name,
            schedule=schedule,
            clock=self.clock,
        )

        self.habit_repo.add(habit)
        return habit

    def list_habits(self) -> list[Habit]:
        return self.habit_repo.list_all()

    # ------------------------------
    # Completions
    # ------------------------------

    def complete_habit(self, habit_id: UUID) -> Completion:
        """Record a completion for the given habit and store it."""
        habit = self.habit_repo.get(habit_id)

        completion, _event = Completion.record(
            habit=habit,
            clock=self.clock,
        )

        self.completion_repo.add(completion)
        return completion

    # ------------------------------
    # Streaks
    # ------------------------------

    def calculate_streak(
        self,
        habit_id: UUID,
        rule: StreakRule | None = None,
    ) -> Streak:
        """Calculate the streak for a habit using the given rule.

        If rule is None, choose one based on the habit's schedule.
        """
        habit = self.habit_repo.get(habit_id)
        completions = self.completion_repo.list_for_habit(habit_id)
        now = self.clock.now()

        if rule is None:
            rule = make_streak_rule(habit.schedule)

        streak = rule.calculate(habit=habit, completions=completions, now=now)
        return streak
