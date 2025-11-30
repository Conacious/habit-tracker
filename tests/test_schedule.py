from __future__ import annotations

import pytest
from habit_tracker.domain import Schedule


def test_basic_schedules() -> None:
    schedules = ["daily", "weekly", "monthly", "times_per_week:3"]
    for schedule in schedules:
        s = Schedule(raw=schedule)

        if schedule == "times_per_week:3":
            assert s.times_per_week == 3

        assert s.raw == schedule


def test_is_daily() -> None:
    s = Schedule(raw="daily")
    assert s.is_daily


def test_is_weekly() -> None:
    s = Schedule(raw="weekly")
    assert s.is_weekly


def test_is_monthly() -> None:
    s = Schedule(raw="monthly")
    assert s.is_monthly


def test_invalid_schedule_is_rejected() -> None:
    invalid_schedules = [
        "",
        "daily2",
        "weekly2",
        "monthly2",
        "times_per_week:0",
        "times_per_week:-7",
        "myownschedule",
    ]
    for schedule in invalid_schedules:
        with pytest.raises(ValueError):
            Schedule(raw=schedule)
