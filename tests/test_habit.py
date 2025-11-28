from __future__ import annotations

from datetime import datetime
from uuid import UUID
from habit_tracker.domain import Habit, HabitCreated, Schedule
from .utils import FakeClock, test_schedule


def test_create_habit_sets_basic_fields() -> None:
    fixed_date = datetime(2025, 1, 1, 10, 0, 0)
    clock = FakeClock(fixed_date)
    event_name = "Drink water"

    habit, event = Habit.create(
        name=event_name,
        schedule=test_schedule,
        clock=clock,
    )

    assert habit.name == event_name
    assert habit.schedule == test_schedule
    assert habit.created_at == fixed_date
    assert habit.is_active is True
    assert isinstance(habit.id, UUID)

    assert isinstance(event, HabitCreated)
    assert event.habit_id == habit.id
    assert event.name == event_name
    assert event.occurred_at == fixed_date


def test_create_habit_rejects_empty_name() -> None:
    fixed_time = datetime(2025, 1, 1, 10, 0, 0)
    clock = FakeClock(fixed_time)

    # Empty / whitespace-only names are not allowed
    for bad_name in ["", "   "]:
        try:
            Habit.create(name=bad_name, schedule=test_schedule, clock=clock)
            assert False, "Expected ValueError for empty habit name"
        except ValueError:
            pass


def test_create_habit_rejects_invalid_schedule() -> None:
    fixed_time = datetime(2025, 1, 1, 10, 0, 0)
    clock = FakeClock(fixed_time)

    for bad_schedule in ["invalid", "invalid2"]:
        try:
            Habit.create(
                name="Drink water", schedule=Schedule(raw=bad_schedule), clock=clock
            )
            assert False, "Expected ValueError for invalid schedule"
        except ValueError:
            pass
