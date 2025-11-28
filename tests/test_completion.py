from __future__ import annotations

from datetime import datetime, timedelta
from uuid import UUID

from habit_tracker.domain.habit import Habit
from habit_tracker.domain.completion import Completion
from habit_tracker.domain.events import HabitCompleted
from .utils import FakeClock, make_habit_and_completion, test_schedule


def test_record_completion_creates_completion_and_event() -> None:
    # Arrange
    created_time = datetime(2025, 1, 1, 10, 0, 0)
    completion_time = datetime(2025, 1, 1, 18, 30, 0)

    clock = FakeClock(created_time)

    habit, completion, event = make_habit_and_completion(
        clock=clock,
        completion_time=completion_time,
        name="Read book",
        schedule=test_schedule,
    )

    # Assert: completion fields
    assert isinstance(completion.id, UUID)
    assert completion.habit_id == habit.id
    assert completion.completed_at == completion_time

    # Assert: event fields
    assert isinstance(event, HabitCompleted)
    assert event.habit_id == habit.id
    assert event.completed_at == completion_time
    assert event.occurred_at == completion_time


def test_multiple_completions_have_different_ids_and_times() -> None:
    base_time = datetime(2025, 1, 1, 8, 0, 0)
    clock = FakeClock(base_time)
    # First completion
    first_time = base_time + timedelta(hours=10)

    _, completion1, _ = make_habit_and_completion(
        clock=clock,
        completion_time=first_time,
        name="Exercise",
        schedule=test_schedule,
    )

    # Second completion (later)
    second_time = base_time + timedelta(days=1, hours=9)

    _, completion2, _ = make_habit_and_completion(
        clock=clock,
        completion_time=second_time,
        name="Exercise",
        schedule=test_schedule,
    )

    assert completion1.id != completion2.id
    assert completion1.completed_at == first_time
    assert completion2.completed_at == second_time
