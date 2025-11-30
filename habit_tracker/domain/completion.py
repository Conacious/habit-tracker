from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from .clock import Clock
from .events import HabitCompleted
from .habit import Habit


@dataclass(frozen=True)
class Completion:
    """Represents a single completion of a habit."""

    id: UUID
    habit_id: UUID
    completed_at: datetime

    @classmethod
    def record(
        cls,
        habit: Habit,
        clock: Clock,
        completion_id: UUID | None = None,
    ) -> tuple[Completion, HabitCompleted]:
        """Record a new completion for the given habit.

        Returns both the Completion entity and the corresponding domain event.
        """
        completed_at = clock.now()
        comp_id = completion_id or uuid4()

        completion = cls(
            id=comp_id,
            habit_id=habit.id,
            completed_at=completed_at,
        )

        event = HabitCompleted(
            occurred_at=completed_at,
            habit_id=habit.id,
            completed_at=completed_at,
        )

        return completion, event
