from __future__ import annotations

from datetime import datetime, timedelta
from uuid import UUID

from habit_tracker.domain.completion import Completion
from habit_tracker.domain.habit import Habit
from habit_tracker.domain.schedule import Schedule
from habit_tracker.domain.streak_rules import DailyStreakRule

from tests.utils import FakeClock


def _create_habit(clock: FakeClock) -> Habit:
    """Helper to handle Habit.create returning Habit or (Habit, Event)."""
    result = Habit.create(
        name="Daily habit",
        user_id=UUID(int=1),
        schedule=Schedule("daily"),
        clock=clock,
    )
    if isinstance(result, tuple):
        habit, _event = result
        return habit
    return result


def _record_completion(habit: Habit, clock: FakeClock) -> Completion:
    """Helper to handle Completion.record returning Completion or (Completion, Event)."""
    result = Completion.record(habit=habit, clock=clock)
    if isinstance(result, tuple):
        completion, _event = result
        return completion
    return result


def test_daily_streak_no_completions() -> None:
    base_time = datetime(2025, 1, 1, 8, 0, 0)
    clock = FakeClock(base_time)
    habit = _create_habit(clock)

    rule = DailyStreakRule()
    streak = rule.calculate(habit=habit, completions=[], now=base_time)

    assert streak.habit_id == habit.id
    assert streak.count == 0
    assert streak.last_completed_at is None


def test_daily_streak_with_consecutive_days() -> None:
    base_time = datetime(2025, 1, 1, 8, 0, 0)
    clock = FakeClock(base_time)
    habit = _create_habit(clock)

    completions: list[Completion] = []

    # Day 1 completion
    day1 = base_time
    clock.set(day1)
    completions.append(_record_completion(habit, clock))

    # Day 2 completion
    day2 = base_time + timedelta(days=1, hours=1)
    clock.set(day2)
    completions.append(_record_completion(habit, clock))

    # Day 3 completion
    day3 = base_time + timedelta(days=2, hours=2)
    clock.set(day3)
    completions.append(_record_completion(habit, clock))

    rule = DailyStreakRule()
    now = day3 + timedelta(hours=1)

    streak = rule.calculate(habit=habit, completions=completions, now=now)

    assert streak.count == 3
    assert streak.last_completed_at == completions[-1].completed_at


def test_daily_streak_break_on_missing_day() -> None:
    base_time = datetime(2025, 1, 1, 8, 0, 0)
    clock = FakeClock(base_time)
    habit = _create_habit(clock)

    completions: list[Completion] = []

    # Day 1 completion
    day1 = base_time
    clock.set(day1)
    completions.append(_record_completion(habit, clock))

    # Skip Day 2

    # Day 3 completion
    day3 = base_time + timedelta(days=2, hours=2)
    clock.set(day3)
    completions.append(_record_completion(habit, clock))

    rule = DailyStreakRule()
    now = day3 + timedelta(hours=1)

    streak = rule.calculate(habit=habit, completions=completions, now=now)

    # Only the last day counts, because there is a gap between day1 and day3.
    assert streak.count == 1
    assert streak.last_completed_at == completions[-1].completed_at
