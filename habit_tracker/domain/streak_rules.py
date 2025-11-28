from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, date
from typing import Protocol, Sequence

from .habit import Habit
from .completion import Completion
from .streak import Streak
from .helpers import _find_last_completion, _find_first_completion


class StreakRule(Protocol):
    """Strategy interface for streak calculation rules."""

    def calculate(
        self,
        habit: Habit,
        completions: Sequence[Completion],
        now: datetime,
    ) -> Streak:
        """Calculate the current streak for the given habit."""
        ...


# ---------------------------------------------------------------------------
# Daily streak rule
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DailyStreakRule:
    """Streak rule where each *day* with at least one completion counts.

    The streak is the number of consecutive days with completions,
    ending at the day of the most recent completion (<= now).
    """

    def calculate(
        self,
        habit: Habit,
        completions: Sequence[Completion],
        now: datetime,
    ) -> Streak:
        # Filter completions to only those belonging to the habit and before "now"
        relevant = [
            c for c in completions if c.habit_id == habit.id and c.completed_at <= now
        ]

        last_completion = _find_last_completion(relevant)

        if not last_completion:
            return Streak(habit_id=habit.id, count=0, last_completed_at=None)

        last_date: date = last_completion.completed_at.date()
        completion_dates = {
            c.completed_at.date() for c in relevant if c.completed_at <= now
        }

        # Count how many consecutive days *before* last_date are also completion days.
        # last_date itself is always counted as 1.
        streak_count = 1
        current_date = last_date - timedelta(days=1)

        while current_date in completion_dates:
            streak_count += 1
            current_date = current_date - timedelta(days=1)

        return Streak(
            habit_id=habit.id,
            count=streak_count,
            last_completed_at=last_completion.completed_at,
        )


# ---------------------------------------------------------------------------
# Times per week rule
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TimesPerWeekStreakRule:
    """Streak rule: complete the habit N times per ISO week.

    The streak is the number of consecutive weeks (ending in the week of the
    most recent completion) where the number of completions >= `times_per_week`.

    ISO week explanation (simplified):
      - Each date has an (ISO year, ISO week number, weekday) triple.
      - We only care about (ISO year, ISO week number) to identify "a week".
    """

    times_per_week: int

    def __post_init__(self) -> None:
        if self.times_per_week <= 0:
            raise ValueError("times_per_week must be positive.")

    def calculate(
        self,
        habit: Habit,
        completions: Sequence[Completion],
        now: datetime,
    ) -> Streak:
        # 1) Filter completions to only those belonging to the habit and before "now"
        relevant = [
            c for c in completions if c.habit_id == habit.id and c.completed_at <= now
        ]

        # 2) Count how many completions happened *per week*.
        #    We use a dictionary:
        #      key   = (iso_year, iso_week)
        #      value = number of completions in that week
        week_counts: dict[tuple[int, int], int] = {}

        for c in relevant:
            d: date = c.completed_at.date()
            iso_year, iso_week, _weekday = d.isocalendar()
            key = (iso_year, iso_week)

            if key not in week_counts:
                week_counts[key] = 0
            week_counts[key] += 1

        # 3) Find the most recent completion (same style as in DailyStreakRule)
        last_completion = _find_last_completion(relevant)

        first_completion = _find_first_completion(relevant)

        if not last_completion or not first_completion:
            return Streak(habit_id=habit.id, count=0, last_completed_at=None)

        # We'll start checking from the week that contains this last completion.
        current_date: date = last_completion.completed_at.date()

        # 4) Walk backwards week-by-week, counting how many consecutive weeks
        #    meet the "times_per_week" requirement.
        streak_count = 0

        while current_date >= first_completion.completed_at.date():
            iso_year, iso_week, _weekday = current_date.isocalendar()
            key = (iso_year, iso_week)

            # How many completions did this week have?
            count_for_week = week_counts.get(key, 0)

            # If this week doesn't meet the requirement, the streak stops.
            if count_for_week < self.times_per_week:
                break

            streak_count += 1

            # Move one week back (7 days earlier, same weekday)
            current_date = current_date - timedelta(days=7)

        return Streak(
            habit_id=habit.id,
            count=streak_count,
            last_completed_at=last_completion.completed_at,
        )


# ---------------------------------------------------------------------------
# At least N days in the last M days rule
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AtLeastNDaysInLastMDaysRule:
    """Streak rule: complete the habit at least N times in the last M days."""

    n: int
    m: int

    def __post_init__(self) -> None:
        if self.n <= 0:
            raise ValueError("n must be positive.")
        if self.m <= 0:
            raise ValueError("m must be positive.")

    def calculate(
        self,
        habit: Habit,
        completions: Sequence[Completion],
        now: datetime,
    ) -> Streak:
        # Filter completions to only those belonging to the habit and before "now"
        relevant = [
            c for c in completions if c.habit_id == habit.id and c.completed_at <= now
        ]

        # Iterate over completions and check if they are at least n times in the last m days
        streak_count = 0
        for c in relevant:
            if c.completed_at >= (now - timedelta(days=self.m)):
                streak_count += 1

        if streak_count < self.n:
            streak_count = 0
        else:
            streak_count = 1

        return Streak(
            habit_id=habit.id,
            count=streak_count,
            last_completed_at=now,
        )
