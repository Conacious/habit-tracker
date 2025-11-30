from __future__ import annotations

from datetime import datetime, timedelta
from uuid import UUID

from habit_tracker.domain.completion import Completion
from habit_tracker.domain.habit import Habit
from habit_tracker.domain.schedule import Schedule
from habit_tracker.domain.streak_rules import TimesPerWeekStreakRule

from tests.utils import FakeClock


def _create_habit(clock: FakeClock, times_per_week: int = 3) -> Habit:
    result = Habit.create(
        name="Weekly habit",
        user_id=UUID(int=1),
        schedule=Schedule(f"times_per_week:{times_per_week}"),
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


def test_times_per_week_no_completions() -> None:
    base_monday = datetime(2025, 1, 6, 9, 0, 0)  # A Monday
    clock = FakeClock(base_monday)
    habit = _create_habit(clock, times_per_week=3)

    rule = TimesPerWeekStreakRule(times_per_week=3)
    streak = rule.calculate(habit=habit, completions=[], now=base_monday)

    assert streak.count == 0
    assert streak.last_completed_at is None


def test_times_per_week_two_good_weeks_in_a_row() -> None:
    base_monday = datetime(2025, 1, 6, 9, 0, 0)  # Monday of "current" week
    prev_monday = base_monday - timedelta(days=7)

    clock = FakeClock(base_monday)
    habit = _create_habit(clock, times_per_week=3)

    completions: list[Completion] = []

    # Previous week — 3 completions (Mon, Wed, Fri)
    for offset in (0, 2, 4):
        when = prev_monday + timedelta(days=offset)
        clock.set(when)
        completions.append(_record_completion(habit, clock))

    # Current week — 3 completions (Mon, Wed, Fri)
    for offset in (0, 2, 4):
        when = base_monday + timedelta(days=offset)
        clock.set(when)
        completions.append(_record_completion(habit, clock))

    rule = TimesPerWeekStreakRule(times_per_week=3)
    now = base_monday + timedelta(days=6, hours=23)  # Sunday night

    streak = rule.calculate(habit=habit, completions=completions, now=now)

    assert streak.count == 2
    assert streak.last_completed_at == max(c.completed_at for c in completions)


def test_times_per_week_break_when_week_below_threshold() -> None:
    base_monday = datetime(2025, 1, 20, 9, 0, 0)  # current week Monday
    prev_monday = base_monday - timedelta(days=7)
    prev2_monday = base_monday - timedelta(days=14)

    clock = FakeClock(base_monday)
    habit = _create_habit(clock, times_per_week=3)

    completions: list[Completion] = []

    # Week -2: 3 completions (good)
    for offset in (0, 2, 4):
        when = prev2_monday + timedelta(days=offset)
        clock.set(when)
        completions.append(_record_completion(habit, clock))

    # Week -1: only 1 completion (bad)
    when = prev_monday  # just Monday
    clock.set(when)
    completions.append(_record_completion(habit, clock))

    # Current week: 3 completions (good)
    for offset in (0, 2, 4):
        when = base_monday + timedelta(days=offset)
        clock.set(when)
        completions.append(_record_completion(habit, clock))

    rule = TimesPerWeekStreakRule(times_per_week=3)
    now = base_monday + timedelta(days=6, hours=23)

    streak = rule.calculate(habit=habit, completions=completions, now=now)

    # Only current week counts; previous week breaks the chain.
    assert streak.count == 1
