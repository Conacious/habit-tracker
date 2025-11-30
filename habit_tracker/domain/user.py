from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from habit_tracker.domain.clock import Clock


@dataclass(frozen=True)
class User:
    id: UUID
    email: str
    hashed_password: str
    created_at: datetime
    is_active: bool = True

    # Classmethod is a method that is bound to the class and not the instance of the class
    # It can modify a class state that applies across all instances of the class
    # It is defined using the @classmethod decorator
    # It takes cls as the first parameter instead of self
    @classmethod
    def create(cls, email: str, hashed_password: str, clock: Clock) -> User:
        return cls(
            id=uuid4(),
            email=email,
            hashed_password=hashed_password,
            created_at=clock.now(),
        )
