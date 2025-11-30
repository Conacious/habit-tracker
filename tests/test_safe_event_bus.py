from __future__ import annotations

from datetime import datetime
from uuid import UUID

import pytest
from habit_tracker.application.services import HabitTrackerService
from habit_tracker.domain.events import HabitCreated
from habit_tracker.domain.schedule import Schedule
from habit_tracker.infrastructure.event_bus import InMemoryEventBus
from habit_tracker.infrastructure.inmemory_repositories import (
    InMemoryCompletionRepository,
    InMemoryHabitRepository,
)

from tests.utils import FakeClock


def test_event_bus_error_handler() -> None:
    def handle_with_error(event: HabitCreated) -> None:
        raise RuntimeError()

    def handle_no_error(event: HabitCreated) -> None:
        return

    bus = InMemoryEventBus()

    bus.subscribe(HabitCreated, handle_with_error)
    bus.subscribe(HabitCreated, handle_no_error)

    habit_repo = InMemoryHabitRepository()
    completion_repo = InMemoryCompletionRepository()

    habit_tracker_service = HabitTrackerService(
        habit_repo=habit_repo,
        completion_repo=completion_repo,
        clock=FakeClock(fixed=datetime(2025, 1, 1, 0, 0)),
        event_bus=bus,
    )

    with pytest.raises(RuntimeError):
        habit_tracker_service.create_habit(
            name="habit", schedule=Schedule(raw="daily"), user_id=UUID(int=1)
        )

    assert len(habit_tracker_service.list_habits_for_user(user_id=UUID(int=1))) == 1
