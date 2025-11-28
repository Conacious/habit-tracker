from __future__ import annotations

from uuid import UUID
from habit_tracker.infrastructure import (
    InMemoryCompletionRepository,
    InMemoryHabitRepository,
)
from habit_tracker.application.services import HabitTrackerService
from habit_tracker.domain.schedule import Schedule
from habit_tracker.domain.events import HabitCompleted
from habit_tracker.infrastructure.event_bus import InMemoryEventBus
from habit_tracker.application.event_bus import EventBus
from habit_tracker.domain.events import DomainEvent
from .utils import CompletionCounter, FakeClock
from datetime import datetime


def test_stateful_subscriber() -> None:
    bus = InMemoryEventBus()
    completion_counter = CompletionCounter()

    bus.subscribe(HabitCompleted, completion_counter.habit_completed)

    habit_repo = InMemoryHabitRepository()
    completion_repo = InMemoryCompletionRepository()
    clock = FakeClock(fixed=datetime(2025, 1, 1, 0, 0))
    habit_tracker_service = HabitTrackerService(
        habit_repo=habit_repo,
        completion_repo=completion_repo,
        clock=clock,
        event_bus=bus,
    )

    habit1 = habit_tracker_service.create_habit(
        name="habit1", schedule=Schedule(raw="daily")
    )
    habit2 = habit_tracker_service.create_habit(
        name="habit2", schedule=Schedule(raw="daily")
    )

    habit_tracker_service.complete_habit(habit_id=habit1.id)
    habit_tracker_service.complete_habit(habit_id=habit2.id)

    assert completion_counter.get_count(habit_id=habit1.id) == 1
    assert completion_counter.get_count(habit_id=habit2.id) == 1
