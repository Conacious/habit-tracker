from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from habit_tracker.application.repositories import HabitRepository, ReminderRepository
from habit_tracker.domain.clock import Clock
from habit_tracker.domain.events import HabitCompleted, HabitCreated
from habit_tracker.domain.reminder import Reminder


@dataclass
class ReminderEventHandler:
    """Handles habit-related events to keep Reminder state up-to-date."""

    habit_repo: HabitRepository
    reminder_repo: ReminderRepository
    clock: Clock

    def on_habit_created(self, event: HabitCreated) -> None:
        """Create an initial reminder when a habit is created."""
        habit = self.habit_repo.get(event.habit_id)
        now = self.clock.now()
        next_due = habit.schedule.next_due_from(now)

        existing = self.reminder_repo.get_by_habit_id(habit.id)
        if existing is not None:
            return

        reminder = Reminder(
            id=uuid4(),
            habit_id=habit.id,
            next_due_at=next_due,
            active=True,
        )
        self.reminder_repo.add(reminder)

    def on_habit_completed(self, event: HabitCompleted) -> None:
        """Move the next_due_at forward when the habit is completed."""
        habit = self.habit_repo.get(event.habit_id)
        now = self.clock.now()
        next_due = habit.schedule.next_due_from(now)

        reminder = self.reminder_repo.get_by_habit_id(habit.id)
        if reminder is None:
            reminder = Reminder(
                id=uuid4(),
                habit_id=habit.id,
                next_due_at=next_due,
                active=True,
            )
        else:
            reminder.next_due_at = next_due

        self.reminder_repo.add(reminder)
