from __future__ import annotations

from datetime import datetime, timedelta

from habit_tracker.domain.habit import Habit
from habit_tracker.domain.schedule import Schedule
from habit_tracker.domain.completion import Completion
from habit_tracker.infrastructure.inmemory_repositories import (
    InMemoryHabitRepository,
    InMemoryCompletionRepository,
)

from tests.utils import FakeClock
from uuid import UUID


def _create_habit(clock: FakeClock) -> Habit:
    result = Habit.create(
        name="Test habit",
        user_id=UUID(int=1),
        schedule=Schedule("daily"),
        clock=clock,
    )
    if isinstance(result, tuple):
        habit, _event = result
        return habit
    return result


def _record_completion(habit: Habit, clock: FakeClock) -> Completion:
    result = Completion.record(habit=habit, clock=clock)
    if isinstance(result, tuple):
        completion, _event = result
        return completion
    return result


def test_inmemory_habit_repository_add_and_get() -> None:
    repo = InMemoryHabitRepository()
    clock = FakeClock(datetime(2025, 1, 1, 9, 0, 0))

    habit = _create_habit(clock)
    repo.add(habit)

    loaded = repo.get(habit.id)
    assert loaded == habit

    all_habits = repo.list_all()
    assert habit in all_habits


def test_inmemory_habit_repository_remove() -> None:
    repo = InMemoryHabitRepository()
    clock = FakeClock(datetime(2025, 1, 1, 9, 0, 0))

    habit = _create_habit(clock)
    repo.add(habit)

    repo.remove(habit.id)

    all_habits = repo.list_all()
    assert habit not in all_habits


def test_inmemory_completion_repository_basic_queries() -> None:
    habit_repo = InMemoryHabitRepository()
    completion_repo = InMemoryCompletionRepository()
    clock = FakeClock(datetime(2025, 1, 1, 9, 0, 0))

    habit = _create_habit(clock)
    habit_repo.add(habit)

    # Create two completions for the same habit
    c1 = _record_completion(habit, clock)

    clock.set(clock.now() + timedelta(days=1))
    c2 = _record_completion(habit, clock)

    completion_repo.add(c1)
    completion_repo.add(c2)

    all_for_habit = completion_repo.list_for_habit(habit.id)
    assert len(all_for_habit) == 2

    start = c1.completed_at
    end = c1.completed_at
    between = completion_repo.list_for_habit_between(
        habit_id=habit.id,
        start=start,
        end=end,
    )
    assert between == [c1]
