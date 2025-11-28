from __future__ import annotations

from datetime import datetime, UTC

from habit_tracker.domain import Clock


class SystemClock(Clock):
    def now(self) -> datetime:
        return datetime.now(tz=UTC)
