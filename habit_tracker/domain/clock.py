from __future__ import annotations

from datetime import datetime
from typing import Protocol


class Clock(Protocol):
    """Clock abstraction to make domain logic testable."""

    def now(self) -> datetime:
        """Return the current date and time."""
        ...
