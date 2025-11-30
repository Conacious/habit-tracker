from __future__ import annotations

from datetime import datetime
from uuid import UUID

from habit_tracker.domain import Completion, Habit, HabitCompleted, Schedule

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
        user_id=UUID(int=1),
        schedule=schedule,
        clock=clock,
    )
    clock.set(completion_time)
    completion, event = Completion.record(habit=habit, clock=clock)

    return habit, completion, event


class CompletionCounter:
    # Map habit_id to number of completions
    counter: dict[UUID, int]

    def __init__(self) -> None:
        self.counter = {}

    def habit_completed(self, event: HabitCompleted) -> None:
        if event.habit_id not in self.counter:
            self.counter[event.habit_id] = 1
        else:
            self.counter[event.habit_id] += 1

    def get_count(self, habit_id: UUID) -> int:
        return self.counter.get(habit_id, 0)
