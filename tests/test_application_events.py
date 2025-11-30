from __future__ import annotations

from datetime import datetime
from typing import List

from habit_tracker.domain.schedule import Schedule
from habit_tracker.domain.events import HabitCreated, HabitCompleted, DomainEvent
from habit_tracker.application.services import HabitTrackerService
from habit_tracker.infrastructure import (
    InMemoryHabitRepository,
    InMemoryCompletionRepository,
    InMemoryEventBus,
)
from tests.utils import FakeClock
from uuid import UUID


def _make_service_with_bus(
    start_time: datetime,
) -> tuple[HabitTrackerService, InMemoryEventBus]:
    clock = FakeClock(start_time)
    habit_repo = InMemoryHabitRepository()
    completion_repo = InMemoryCompletionRepository()
    bus = InMemoryEventBus()

    service = HabitTrackerService(
        habit_repo=habit_repo,
        completion_repo=completion_repo,
        clock=clock,
        event_bus=bus,
    )

    return service, bus


def test_create_habit_publishes_habit_created_event() -> None:
    start_time = datetime(2025, 1, 1, 9, 0, 0)
    service, bus = _make_service_with_bus(start_time)

    received: List[DomainEvent] = []

    def handler(event: DomainEvent) -> None:
        received.append(event)

    bus.subscribe(HabitCreated, handler)

    habit = service.create_habit(
        name="Read", schedule=Schedule("daily"), user_id=UUID(int=1)
    )

    assert len(received) == 1
    event = received[0]
    assert isinstance(event, HabitCreated)
    assert event.habit_id == habit.id


def test_complete_habit_publishes_habit_completed_event() -> None:
    start_time = datetime(2025, 1, 1, 9, 0, 0)
    service, bus = _make_service_with_bus(start_time)

    # subscribe before any events
    received: List[DomainEvent] = []

    def handler(event: DomainEvent) -> None:
        received.append(event)

    bus.subscribe(HabitCompleted, handler)

    habit = service.create_habit(
        name="Exercise", schedule=Schedule("daily"), user_id=UUID(int=1)
    )
    service.complete_habit(habit.id, user_id=UUID(int=1))

    assert len(received) == 1
    event = received[0]
    assert isinstance(event, HabitCompleted)
    assert event.habit_id == habit.id
