from .clock import Clock
from .habit import Habit
from .completion import Completion
from .events import DomainEvent, HabitCompleted, HabitCreated
from .event_collector import EventCollector
from .schedule import Schedule
from .streak import Streak
from .streak_rules import (
    StreakRule,
    DailyStreakRule,
    TimesPerWeekStreakRule,
    AtLeastNDaysInLastMDaysRule,
)
from .helpers import _find_last_completion, _find_first_completion

__all__ = [
    "Clock",
    "Habit",
    "Completion",
    "DomainEvent",
    "HabitCompleted",
    "HabitCreated",
    "Schedule",
    "EventCollector",
    "Streak",
    "StreakRule",
    "DailyStreakRule",
    "TimesPerWeekStreakRule",
    "_find_last_completion",
    "_find_first_completion",
]

# This makes it a bit nicer to import from habit_tracker.domain
# from habit_tracker.domain import Habit, Completion, HabitCompleted
