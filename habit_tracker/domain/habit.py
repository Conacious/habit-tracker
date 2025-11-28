from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from .events import HabitCreated
from .clock import Clock
from .schedule import Schedule


@dataclass(frozen=True)
class Habit:
    id: UUID
    name: str
    schedule: Schedule
    created_at: datetime
    is_active: bool = True

    @classmethod
    def create(
        cls,
        name: str,
        schedule: Schedule,
        clock: Clock,
        habit_id: Optional[UUID] = None,
    ) -> tuple[Habit, HabitCreated]:
        """Factory method to create a new Habit using an injected clock."""
        habit_name = name.strip()
        if not habit_name:
            raise ValueError("Habit name must not be empty.")

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
                name=habit_name,
                schedule=schedule,
                created_at=created_at,
                is_active=True,
            ),
            event,
        )
