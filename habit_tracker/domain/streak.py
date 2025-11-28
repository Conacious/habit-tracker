from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class Streak:
    """Represents the current streak for a habit.

    - count: how many consecutive periods (days/weeks) the rule considers "met".
    - last_completed_at: time of the most recent completion that contributed to this streak.
    """

    habit_id: UUID
    count: int
    last_completed_at: Optional[datetime]

    def is_at_least(self, minimum: int) -> bool:
        if minimum <= 0:
            raise ValueError("minimum must be positive")
        return self.count >= minimum
