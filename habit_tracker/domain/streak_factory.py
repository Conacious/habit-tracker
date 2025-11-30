from habit_tracker.domain.schedule import Schedule
from habit_tracker.domain.streak_rules import (
    DailyStreakRule,
    StreakRule,
    TimesPerWeekStreakRule,
)


def make_streak_rule(schedule: Schedule) -> StreakRule:
    """
    Create the appropriate StreakRule for a given Schedule.

    :param schedule: The schedule configuration.
    :return: A StreakRule instance.
    :raises ValueError: If the schedule type is not supported for streaks.
    """
    if schedule.is_daily:
        return DailyStreakRule()

    if schedule.raw.startswith("times_per_week:"):
        return TimesPerWeekStreakRule(times_per_week=schedule.times_per_week)

    raise ValueError(f"Unsupported schedule for streaks: {schedule.raw}")
