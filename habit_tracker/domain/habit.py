from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from .clock import Clock
from .events import HabitCreated
from .schedule import Schedule


@dataclass(frozen=True)
class Habit:
    id: UUID
    user_id: UUID
    name: str
    schedule: Schedule
    created_at: datetime
    is_active: bool = True

    @classmethod
    def create(
        cls,
        name: str,
        user_id: UUID,
        schedule: Schedule,
        clock: Clock,
        habit_id: UUID | None = None,
    ) -> tuple[Habit, HabitCreated]:
        """Factory method to create a new Habit using an injected clock."""
        habit_name = name.strip()
        if not habit_name:
            raise ValueError("Habit name must not be empty.")

        if not user_id:
            raise ValueError("User ID must not be empty.")

        habit_uuid = habit_id or uuid4()
        created_at = clock.now()

        event = HabitCreated(
            occurred_at=created_at,
            habit_id=habit_uuid,
            name=habit_name,
        )

        return (
            cls(
                id=habit_uuid,
                user_id=user_id,
                name=habit_name,
                schedule=schedule,
                created_at=created_at,
                is_active=True,
            ),
            event,
        )
