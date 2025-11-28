from __future__ import annotations

from datetime import datetime, timedelta

from habit_tracker.domain.schedule import Schedule


def test_daily_schedule_next_due_is_next_day() -> None:
    now = datetime(2025, 1, 1, 9, 0, 0)
    schedule = Schedule("daily")

    next_due = schedule.next_due_from(now)

    assert next_due == now + timedelta(days=1)


def test_times_per_week_next_due_is_next_day() -> None:
    now = datetime(2025, 1, 1, 9, 0, 0)
    schedule = Schedule("times_per_week:3")

    next_due = schedule.next_due_from(now)

    assert next_due == now + timedelta(days=1)
