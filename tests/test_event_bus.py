from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from habit_tracker.domain.events import DomainEvent, HabitCompleted, HabitCreated
from habit_tracker.infrastructure.event_bus import InMemoryEventBus


def test_event_bus_calls_subscribed_handler() -> None:
    bus = InMemoryEventBus()
    received: list[DomainEvent] = []

    def handler(event: DomainEvent) -> None:
        received.append(event)

    bus.subscribe(HabitCompleted, handler)

    event = HabitCompleted(
        occurred_at=datetime(2025, 1, 1, 10, 0, 0),
        habit_id=uuid4(),
        completed_at=datetime(2025, 1, 1, 10, 0, 0),
    )

    bus.publish(event)

    assert len(received) == 1
    assert received[0] is event


def test_event_bus_two_handlers_same_event() -> None:
    bus = InMemoryEventBus()
    received_1: list[DomainEvent] = []
    received_2: list[DomainEvent] = []

    def handler_1(event: DomainEvent) -> None:
        received_1.append(event)

    def handler_2(event: DomainEvent) -> None:
        received_2.append(event)

    bus.subscribe(HabitCompleted, handler_1)
    bus.subscribe(HabitCompleted, handler_2)

    event = HabitCompleted(
        datetime(2025, 1, 1, 0, 0),
        habit_id=uuid4(),
        completed_at=datetime(2025, 1, 1, 1, 0),
    )

    bus.publish(event)

    assert len(received_1) == 1
    assert len(received_2) == 1


def test_handler_not_called_different_event() -> None:
    bus = InMemoryEventBus()
    received: list[DomainEvent] = []

    def handler(event: DomainEvent) -> None:
        received.append(event)

    bus.subscribe(HabitCompleted, handler)

    event = HabitCreated(
        occurred_at=datetime(2025, 1, 1, 1, 0),
        habit_id=uuid4(),
        name="habit",
    )

    bus.publish(event)

    assert len(received) == 0
