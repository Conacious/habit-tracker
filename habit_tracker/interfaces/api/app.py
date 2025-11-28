from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel

from habit_tracker.application.services import HabitTrackerService
from habit_tracker.domain.schedule import Schedule
from habit_tracker.domain.streak import Streak
from habit_tracker.infrastructure.inmemory_repositories import (
    InMemoryHabitRepository,
    InMemoryCompletionRepository,
)
from habit_tracker.infrastructure.clock import SystemClock


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


# --------------------------
# Dependency injection
# --------------------------


def get_service(request: Request) -> HabitTrackerService:
    service = getattr(request.app.state, "service", None)
    if service is None:
        raise RuntimeError("HabitTrackerService not configured on app.state.service")
    return service


# --------------------------
# App factory
# --------------------------


def create_app() -> FastAPI:
    """Create a FastAPI app wired with in-memory repositories and SystemClock."""
    habit_repo = InMemoryHabitRepository()
    completion_repo = InMemoryCompletionRepository()
    clock = SystemClock()

    service = HabitTrackerService(
        habit_repo=habit_repo,
        completion_repo=completion_repo,
        clock=clock,
    )

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

    return app


# Default app for uvicorn ("module:app")
app = create_app()
