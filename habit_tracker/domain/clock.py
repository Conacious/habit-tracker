from __future__ import annotations

from datetime import datetime


class Clock:
    """Clock abstraction to make domain logic testable."""

    def now(self) -> datetime:
        """Return the current date and time."""
        ...
