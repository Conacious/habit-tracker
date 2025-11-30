import pytest
from habit_tracker.domain.schedule import Schedule
from habit_tracker.domain.streak_factory import make_streak_rule
from habit_tracker.domain.streak_rules import DailyStreakRule, TimesPerWeekStreakRule


def test_make_streak_rule_daily():
    schedule = Schedule("daily")
    rule = make_streak_rule(schedule)
    assert isinstance(rule, DailyStreakRule)


def test_make_streak_rule_times_per_week():
    schedule = Schedule("times_per_week:3")
    rule = make_streak_rule(schedule)
    assert isinstance(rule, TimesPerWeekStreakRule)
    assert rule.times_per_week == 3


def test_make_streak_rule_unsupported():
    schedule = Schedule("weekly")
    with pytest.raises(ValueError, match="Unsupported schedule for streaks: weekly"):
        make_streak_rule(schedule)


def test_make_streak_rule_unknown():
    # Schedule itself might allow other strings if we bypass validation or add new ones,
    # but factory should be strict.
    # However, Schedule validation prevents arbitrary strings usually.
    # Let's test with 'monthly' which is valid in Schedule but unsupported in factory.
    schedule = Schedule("monthly")
    with pytest.raises(ValueError, match="Unsupported schedule for streaks: monthly"):
        make_streak_rule(schedule)
