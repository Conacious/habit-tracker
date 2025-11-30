from datetime import datetime
from uuid import UUID, uuid4

import pytest
from habit_tracker.domain.completion import Completion
from habit_tracker.domain.habit import Habit
from habit_tracker.domain.schedule import Schedule
from habit_tracker.domain.streak_rules import AtLeastNDaysInLastMDaysRule


def test_init_validation():
    with pytest.raises(ValueError, match="n must be positive"):
        AtLeastNDaysInLastMDaysRule(n=0, m=7)

    with pytest.raises(ValueError, match="m must be positive"):
        AtLeastNDaysInLastMDaysRule(n=1, m=0)

    rule = AtLeastNDaysInLastMDaysRule(n=1, m=7)
    assert rule.n == 1
    assert rule.m == 7


def test_calculate_not_enough():
    rule = AtLeastNDaysInLastMDaysRule(n=3, m=7)
    habit = Habit(
        id=uuid4(),
        user_id=UUID(int=1),
        name="Test Habit",
        schedule=Schedule("daily"),
        created_at=datetime(2023, 1, 1),
    )
    now = datetime(2023, 1, 10, 12, 0, 0)

    # 2 completions in the last 7 days
    c1 = Completion(
        id=uuid4(), habit_id=habit.id, completed_at=datetime(2023, 1, 10, 10, 0)
    )
    c2 = Completion(
        id=uuid4(), habit_id=habit.id, completed_at=datetime(2023, 1, 9, 10, 0)
    )

    streak = rule.calculate(habit, [c1, c2], now)

    assert streak.count == 0
    # The current implementation sets last_completed_at to now regardless of streak count
    assert streak.last_completed_at == now


def test_calculate_enough():
    rule = AtLeastNDaysInLastMDaysRule(n=3, m=7)
    habit = Habit(
        id=uuid4(),
        user_id=UUID(int=1),
        name="Test Habit",
        schedule=Schedule("daily"),
        created_at=datetime(2023, 1, 1),
    )
    now = datetime(2023, 1, 10, 12, 0, 0)

    # 3 completions in the last 7 days
    c1 = Completion(
        id=uuid4(), habit_id=habit.id, completed_at=datetime(2023, 1, 10, 10, 0)
    )
    c2 = Completion(
        id=uuid4(), habit_id=habit.id, completed_at=datetime(2023, 1, 9, 10, 0)
    )
    c3 = Completion(
        id=uuid4(), habit_id=habit.id, completed_at=datetime(2023, 1, 5, 10, 0)
    )

    streak = rule.calculate(habit, [c1, c2, c3], now)

    assert streak.count == 1
    assert streak.last_completed_at == now


def test_calculate_outside_window():
    rule = AtLeastNDaysInLastMDaysRule(n=1, m=3)  # Last 3 days (72 hours)
    habit = Habit(
        id=uuid4(),
        user_id=UUID(int=1),
        name="Test Habit",
        schedule=Schedule("daily"),
        created_at=datetime(2023, 1, 1),
    )
    now = datetime(2023, 1, 10, 12, 0, 0)

    # Completion 4 days ago (outside 3 day window)
    c1 = Completion(
        id=uuid4(), habit_id=habit.id, completed_at=datetime(2023, 1, 6, 12, 0, 0)
    )

    streak = rule.calculate(habit, [c1], now)

    assert streak.count == 0
    assert streak.last_completed_at == now


def test_calculate_exact_boundary():
    rule = AtLeastNDaysInLastMDaysRule(n=1, m=1)  # Last 24 hours
    habit = Habit(
        id=uuid4(),
        user_id=UUID(int=1),
        name="Test Habit",
        schedule=Schedule("daily"),
        created_at=datetime(2023, 1, 1),
    )
    now = datetime(2023, 1, 10, 12, 0, 0)

    # Completion exactly 24 hours ago (should be included as >=)
    c1 = Completion(
        id=uuid4(), habit_id=habit.id, completed_at=datetime(2023, 1, 9, 12, 0, 0)
    )

    streak = rule.calculate(habit, [c1], now)

    assert streak.count == 1
    assert streak.last_completed_at == now

    # Completion 24 hours + 1 second ago (should be excluded)
    c2 = Completion(
        id=uuid4(), habit_id=habit.id, completed_at=datetime(2023, 1, 9, 11, 59, 59)
    )

    streak = rule.calculate(habit, [c2], now)

    assert streak.count == 0
