from __future__ import annotations

from datetime import datetime
from uuid import UUID

from habit_tracker.domain import _find_first_completion, _find_last_completion
from habit_tracker.domain.completion import Completion

completions = [
    Completion(id=UUID(int=1), habit_id=UUID(int=1), completed_at=datetime(2023, 1, 1)),
    Completion(id=UUID(int=2), habit_id=UUID(int=1), completed_at=datetime(2023, 1, 2)),
    Completion(id=UUID(int=3), habit_id=UUID(int=1), completed_at=datetime(2023, 1, 3)),
]


def test_find_last_completion():
    assert _find_last_completion(completions) == completions[-1]


def test_find_first_completion():
    assert _find_first_completion(completions) == completions[0]
