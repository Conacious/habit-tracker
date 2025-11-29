from __future__ import annotations

import sqlite3
from dataclasses import asdict
from datetime import datetime
from typing import List
from uuid import UUID

from habit_tracker.domain.habit import Habit
from habit_tracker.domain.completion import Completion
from habit_tracker.domain.reminder import Reminder
from habit_tracker.domain.schedule import Schedule
from habit_tracker.application.repositories import (
    HabitRepository,
    CompletionRepository,
    ReminderRepository,
)


def _ensure_foreign_keys(conn: sqlite3.Connection) -> None:
    # SQLite requires this PRAGMA per connection
    conn.execute("PRAGMA foreign_keys = ON")


def _create_schema(conn: sqlite3.Connection) -> None:
    """Create tables if they do not exist."""
    _ensure_foreign_keys(conn)

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS habits (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            schedule TEXT NOT NULL,
            created_at TEXT NOT NULL,
            is_active INTEGER NOT NULL
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS completions (
            id TEXT PRIMARY KEY,
            habit_id TEXT NOT NULL,
            completed_at TEXT NOT NULL,
            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS reminders (
            id TEXT PRIMARY KEY,
            habit_id TEXT NOT NULL UNIQUE,
            next_due_at TEXT NOT NULL,
            active INTEGER NOT NULL,
            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
        )
        """
    )

    conn.commit()


def _uuid_to_str(value: UUID) -> str:
    return str(value)


def _uuid_from_str(value: str) -> UUID:
    return UUID(value)


def _dt_to_str(dt: datetime) -> str:
    return dt.isoformat()


def _dt_from_str(value: str) -> datetime:
    return datetime.fromisoformat(value)


class SQLiteHabitRepository(HabitRepository):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn
        _create_schema(self._conn)

    def add(self, habit: Habit) -> None:
        self._conn.execute(
            """
            INSERT INTO habits (id, name, schedule, created_at, is_active)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name=excluded.name,
                schedule=excluded.schedule,
                created_at=excluded.created_at,
                is_active=excluded.is_active
            """,
            (
                _uuid_to_str(habit.id),
                habit.name,
                habit.schedule.raw,
                _dt_to_str(habit.created_at),
                1 if habit.is_active else 0,
            ),
        )
        self._conn.commit()

    def get(self, habit_id: UUID) -> Habit:
        cur = self._conn.execute(
            "SELECT id, name, schedule, created_at, is_active FROM habits WHERE id = ?",
            (_uuid_to_str(habit_id),),
        )
        row = cur.fetchone()
        if row is None:
            raise KeyError(f"Habit {habit_id} not found")

        id_str, name, schedule_raw, created_at_str, is_active_int = row
        return Habit(
            id=_uuid_from_str(id_str),
            name=name,
            schedule=Schedule(schedule_raw),
            created_at=_dt_from_str(created_at_str),
            is_active=bool(is_active_int),
        )

    def list_all(self) -> List[Habit]:
        cur = self._conn.execute(
            "SELECT id, name, schedule, created_at, is_active FROM habits"
        )
        habits: List[Habit] = []
        for id_str, name, schedule_raw, created_at_str, is_active_int in cur.fetchall():
            habits.append(
                Habit(
                    id=_uuid_from_str(id_str),
                    name=name,
                    schedule=Schedule(schedule_raw),
                    created_at=_dt_from_str(created_at_str),
                    is_active=bool(is_active_int),
                )
            )
        return habits

    def remove(self, habit_id: UUID) -> None:
        self._conn.execute(
            "DELETE FROM habits WHERE id = ?",
            (_uuid_to_str(habit_id),),
        )
        self._conn.commit()


class SQLiteCompletionRepository(CompletionRepository):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn
        _create_schema(self._conn)

    def add(self, completion: Completion) -> None:
        self._conn.execute(
            """
            INSERT INTO completions (id, habit_id, completed_at)
            VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                habit_id = excluded.habit_id,
                completed_at = excluded.completed_at
            """,
            (
                _uuid_to_str(completion.id),
                _uuid_to_str(completion.habit_id),
                _dt_to_str(completion.completed_at),
            ),
        )
        self._conn.commit()

    def list_for_habit(self, habit_id: UUID) -> List[Completion]:
        cur = self._conn.execute(
            """
            SELECT id, habit_id, completed_at
            FROM completions
            WHERE habit_id = ?
            ORDER BY completed_at
            """,
            (_uuid_to_str(habit_id),),
        )
        completions: List[Completion] = []
        for id_str, habit_id_str, completed_at_str in cur.fetchall():
            completions.append(
                Completion(
                    id=_uuid_from_str(id_str),
                    habit_id=_uuid_from_str(habit_id_str),
                    completed_at=_dt_from_str(completed_at_str),
                )
            )
        return completions

    def list_for_habit_between(
        self,
        habit_id: UUID,
        start: datetime,
        end: datetime,
    ) -> List[Completion]:
        cur = self._conn.execute(
            """
            SELECT id, habit_id, completed_at
            FROM completions
            WHERE habit_id = ?
              AND completed_at BETWEEN ? AND ?
            ORDER BY completed_at
            """,
            (
                _uuid_to_str(habit_id),
                _dt_to_str(start),
                _dt_to_str(end),
            ),
        )
        completions: List[Completion] = []
        for id_str, habit_id_str, completed_at_str in cur.fetchall():
            completions.append(
                Completion(
                    id=_uuid_from_str(id_str),
                    habit_id=_uuid_from_str(habit_id_str),
                    completed_at=_dt_from_str(completed_at_str),
                )
            )
        return completions


class SQLiteReminderRepository(ReminderRepository):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn
        _create_schema(self._conn)

    def add(self, reminder: Reminder) -> None:
        self._conn.execute(
            """
            INSERT INTO reminders (id, habit_id, next_due_at, active)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(habit_id) DO UPDATE SET
                id = excluded.id,
                next_due_at = excluded.next_due_at,
                active = excluded.active
            """,
            (
                _uuid_to_str(reminder.id),
                _uuid_to_str(reminder.habit_id),
                _dt_to_str(reminder.next_due_at),
                1 if reminder.active else 0,
            ),
        )
        self._conn.commit()

    def get_by_habit_id(self, habit_id: UUID) -> Reminder | None:
        cur = self._conn.execute(
            """
            SELECT id, habit_id, next_due_at, active
            FROM reminders
            WHERE habit_id = ?
            """,
            (_uuid_to_str(habit_id),),
        )
        row = cur.fetchone()
        if row is None:
            return None

        id_str, habit_id_str, next_due_at_str, active_int = row
        return Reminder(
            id=_uuid_from_str(id_str),
            habit_id=_uuid_from_str(habit_id_str),
            next_due_at=_dt_from_str(next_due_at_str),
            active=bool(active_int),
        )

    def list_due(self, before: datetime) -> List[Reminder]:
        cur = self._conn.execute(
            """
            SELECT id, habit_id, next_due_at, active
            FROM reminders
            WHERE active = 1 AND next_due_at <= ?
            """,
            (_dt_to_str(before),),
        )
        reminders: List[Reminder] = []
        for id_str, habit_id_str, next_due_at_str, active_int in cur.fetchall():
            reminders.append(
                Reminder(
                    id=_uuid_from_str(id_str),
                    habit_id=_uuid_from_str(habit_id_str),
                    next_due_at=_dt_from_str(next_due_at_str),
                    active=bool(active_int),
                )
            )
        return reminders
