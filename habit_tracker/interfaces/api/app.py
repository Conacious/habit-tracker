from __future__ import annotations

from habit_tracker.infrastructure.sqlite_repositories import (
    SQLiteCompletionRepository,
    SQLiteHabitRepository,
    SQLiteReminderRepository,
)

from dataclasses import asdict
from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import FastAPI, HTTPException, Depends, Request, Query
from pydantic import BaseModel

from habit_tracker.application.services import HabitTrackerService
from habit_tracker.domain.schedule import Schedule
from habit_tracker.domain.streak import Streak
from habit_tracker.infrastructure.inmemory_repositories import (
    InMemoryHabitRepository,
    InMemoryCompletionRepository,
    InMemoryReminderRepository,
)
from habit_tracker.application import (
    HabitRepository,
    CompletionRepository,
    ReminderRepository,
)
from habit_tracker.infrastructure.clock import SystemClock
from habit_tracker.infrastructure.event_bus import InMemoryEventBus
from habit_tracker.application.reminder_handlers import ReminderEventHandler
from habit_tracker.domain.events import HabitCreated, HabitCompleted
import os
import sqlite3


# --------------------------
# Pydantic DTOs
# --------------------------


class HabitCreate(BaseModel):
    name: str
    schedule: str  # e.g. "daily", "times_per_week:3"


class HabitRead(BaseModel):
    id: UUID
    name: str
    schedule: str
    is_active: bool


class CompletionRead(BaseModel):
    id: UUID
    habit_id: UUID
    completed_at: datetime


class StreakRead(BaseModel):
    habit_id: UUID
    count: int
    last_completed_at: datetime | None


class ReminderRead(BaseModel):
    id: UUID
    habit_id: UUID
    next_due_at: datetime
    active: bool


# --------------------------
# Dependency injection
# --------------------------


def get_service(request: Request) -> HabitTrackerService:
    service = getattr(request.app.state, "service", None)
    if service is None:
        raise RuntimeError("HabitTrackerService not configured on app.state.service")
    return service


# --------------------------
# Auxiliary functions
# --------------------------


def _get_database_mode() -> str:
    return os.getenv("DATABASE_MODE", "sqlite")  # Availble options: inmemory, sqlite


# --------------------------
# Repositories factory
# --------------------------


def _build_repositories() -> (
    tuple[HabitRepository, CompletionRepository, ReminderRepository]
):
    database_mode = _get_database_mode()

    if database_mode == "inmemory":
        return (
            InMemoryHabitRepository(),
            InMemoryCompletionRepository(),
            InMemoryReminderRepository(),
        )

    if database_mode == "sqlite":
        db_path = os.getenv("HABIT_DB_PATH", "habit_tracker.db")
        conn = sqlite3.connect(db_path, check_same_thread=False)
        return (
            SQLiteHabitRepository(conn),
            SQLiteCompletionRepository(conn),
            SQLiteReminderRepository(conn),
        )

    raise ValueError(f"Unknown database mode: {database_mode}")


# --------------------------
# App factory
# --------------------------


def create_app() -> FastAPI:
    """Create a FastAPI app wired with in-memory/sqlite (based on DATABASE_MODE env var) repositories and SystemClock."""
    habit_repo, completion_repo, reminder_repo = _build_repositories()
    clock = SystemClock()
    event_bus = InMemoryEventBus()

    service = HabitTrackerService(
        habit_repo=habit_repo,
        completion_repo=completion_repo,
        reminder_repo=reminder_repo,
        clock=clock,
        event_bus=event_bus,
    )

    reminder_handler = ReminderEventHandler(
        habit_repo=habit_repo,
        reminder_repo=reminder_repo,
        clock=clock,
    )
    event_bus.subscribe(HabitCreated, reminder_handler.on_habit_created)
    event_bus.subscribe(HabitCompleted, reminder_handler.on_habit_completed)

    app = FastAPI(title="Habit Tracker API", version="0.1.0")

    # Attach the service to app state so dependencies can access it
    app.state.service = service

    # ---------- Routes ----------

    @app.post("/habits", response_model=HabitRead, status_code=201)
    def create_habit(
        payload: HabitCreate,
        service: HabitTrackerService = Depends(get_service),
    ) -> HabitRead:
        schedule = Schedule(payload.schedule)
        habit = service.create_habit(name=payload.name, schedule=schedule)
        return HabitRead(
            id=habit.id,
            name=habit.name,
            schedule=habit.schedule.raw,
            is_active=habit.is_active,
        )

    @app.get("/habits", response_model=List[HabitRead])
    def list_habits(
        service: HabitTrackerService = Depends(get_service),
    ) -> List[HabitRead]:
        habits = service.list_habits()
        return [
            HabitRead(
                id=h.id,
                name=h.name,
                schedule=h.schedule.raw,
                is_active=h.is_active,
            )
            for h in habits
        ]

    @app.post("/habits/{habit_id}/complete", response_model=CompletionRead)
    def complete_habit(
        habit_id: UUID,
        service: HabitTrackerService = Depends(get_service),
    ) -> CompletionRead:
        try:
            completion = service.complete_habit(habit_id)
        except KeyError:
            raise HTTPException(status_code=404, detail="Habit not found")
        return CompletionRead(
            id=completion.id,
            habit_id=completion.habit_id,
            completed_at=completion.completed_at,
        )

    @app.get("/habits/{habit_id}/streak", response_model=StreakRead)
    def get_streak(
        habit_id: UUID,
        service: HabitTrackerService = Depends(get_service),
    ) -> StreakRead:
        try:
            streak = service.calculate_streak(habit_id=habit_id)
        except KeyError:
            raise HTTPException(status_code=404, detail="Habit not found")

        return StreakRead(
            habit_id=streak.habit_id,
            count=streak.count,
            last_completed_at=streak.last_completed_at,
        )

    @app.get("/habits/{habit_id}/reminder", response_model=ReminderRead)
    def get_habit_reminder(
        habit_id: UUID,
        service: HabitTrackerService = Depends(get_service),
    ) -> ReminderRead:
        reminder = service.get_reminder(habit_id)
        if reminder is None:
            raise HTTPException(status_code=404, detail="Reminder not found for habit")
        return ReminderRead(
            id=reminder.id,
            habit_id=reminder.habit_id,
            next_due_at=reminder.next_due_at,
            active=reminder.active,
        )

    @app.get("/reminders/due", response_model=List[ReminderRead])
    def list_due_reminders(
        before: datetime | None = Query(
            default=None,
            description="Return reminders with next_due_at <= this time (defaults to now).",
        ),
        service: HabitTrackerService = Depends(get_service),
    ) -> List[ReminderRead]:
        if before is None:
            before = datetime.utcnow()

        reminders = service.list_due_reminders(before)
        return [
            ReminderRead(
                id=r.id,
                habit_id=r.habit_id,
                next_due_at=r.next_due_at,
                active=r.active,
            )
            for r in reminders
        ]

    return app


# Default app for uvicorn ("module:app")
app = create_app()
