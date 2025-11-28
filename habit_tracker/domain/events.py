from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class DomainEvent:
    """Base type for all domain events"""

    occurred_at: datetime


@dataclass(frozen=True)
class HabitCompleted(DomainEvent):
    """Event raised when a habit is completed"""

    habit_id: UUID
    completed_at: datetime


@dataclass(frozen=True)
class HabitCreated(DomainEvent):
    habit_id: UUID
    name: str
