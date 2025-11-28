from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Reminder:
    """Represents the next reminder for a habit.

    We keep it simple:
      - one Reminder per habit
      - 'next_due_at' = next time a reminder should fire
      - 'active' allows disabling reminders later if needed
    """

    id: UUID
    habit_id: UUID
    next_due_at: datetime
    active: bool = True
