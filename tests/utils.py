from __future__ import annotations

from datetime import datetime
from habit_tracker.domain import Habit, Completion, Schedule, HabitCompleted

test_schedule = Schedule(raw="daily")


class FakeClock:
    def __init__(self, fixed: datetime) -> None:
        self._fixed = fixed

    def now(self) -> datetime:
        return self._fixed

    def set(self, new_time: datetime) -> None:
        self._fixed = new_time


def make_habit_and_completion(
    clock: FakeClock,
    completion_time: datetime,
    name: str,
    schedule: Schedule,
) -> tuple[Habit, Completion, HabitCompleted]:
    habit, _ = Habit.create(
        name=name,
        schedule=schedule,
        clock=clock,
    )
    clock.set(completion_time)
    completion, event = Completion.record(habit=habit, clock=clock)

    return habit, completion, event
