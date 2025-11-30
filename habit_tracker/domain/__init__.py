from .clock import Clock
from .completion import Completion
from .event_collector import EventCollector
from .events import DomainEvent, HabitCompleted, HabitCreated
from .habit import Habit
from .helpers import _find_first_completion, _find_last_completion
from .reminder import Reminder
from .schedule import Schedule
from .streak import Streak
from .streak_rules import (
    AtLeastNDaysInLastMDaysRule,
    DailyStreakRule,
    StreakRule,
    TimesPerWeekStreakRule,
)
from .user import User

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
    "AtLeastNDaysInLastMDaysRule",
    "Reminder",
    "_find_last_completion",
    "_find_first_completion",
    "User",
]

# This makes it a bit nicer to import from habit_tracker.domain
# from habit_tracker.domain import Habit, Completion, HabitCompleted
