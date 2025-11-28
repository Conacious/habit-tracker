from __future__ import annotations

from datetime import datetime
from uuid import UUID

from habit_tracker.domain.schedule import Schedule
from habit_tracker.domain.streak_rules import DailyStreakRule
from habit_tracker.application.services import HabitTrackerService
from habit_tracker.infrastructure.inmemory_repositories import (
    InMemoryHabitRepository,
    InMemoryCompletionRepository,
)
from tests.utils import FakeClock


def _make_service(start_time: datetime) -> HabitTrackerService:
    clock = FakeClock(start_time)
    habit_repo = InMemoryHabitRepository()
    completion_repo = InMemoryCompletionRepository()
    return HabitTrackerService(
        habit_repo=habit_repo,
        completion_repo=completion_repo,
        clock=clock,
    )


def test_create_and_list_habits_via_service() -> None:
    start_time = datetime(2025, 1, 1, 9, 0, 0)
    service = _make_service(start_time)

    schedule = Schedule("daily")
    habit = service.create_habit(name="Read", schedule=schedule)

    habits = service.list_habits()
    assert len(habits) == 1
    assert habits[0].id == habit.id


def test_complete_habit_and_calculate_daily_streak() -> None:
    start_time = datetime(2025, 1, 1, 9, 0, 0)
    service = _make_service(start_time)

    schedule = Schedule("daily")
    habit = service.create_habit(name="Exercise", schedule=schedule)

    # Complete the habit once
    completion = service.complete_habit(habit.id)
    assert completion.habit_id == habit.id

    # With one completion on the current day, streak should be 1
    streak = service.calculate_streak(habit_id=habit.id, rule=DailyStreakRule())
    assert streak.count == 1
    assert streak.habit_id == habit.id
    assert streak.last_completed_at == completion.completed_at
