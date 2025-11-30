from __future__ import annotations

from datetime import datetime
from habit_tracker.domain import EventCollector, Habit, Schedule
from .utils import FakeClock
from uuid import UUID


def test_collect_adds_event_to_collector() -> None:
    clock = FakeClock(datetime(2025, 1, 1, 10, 0, 0))
    habit, event = Habit.create(
        name="Drink water",
        user_id=UUID(int=1),
        schedule=Schedule(raw="daily"),
        clock=clock,
    )

    collector = EventCollector()
    collector.collect(event)

    assert collector.events == [event]


def test_collect_returns_copy() -> None:
    clock = FakeClock(datetime(2025, 1, 1, 10, 0, 0))
    habit, event = Habit.create(
        name="Drink water",
        user_id=UUID(int=1),
        schedule=Schedule(raw="daily"),
        clock=clock,
    )

    collector = EventCollector()
    collector.collect(event)

    events = collector.events
    events.clear()
    assert collector.events == [event]
