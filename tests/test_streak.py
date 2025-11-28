from __future__ import annotations

import pytest
from uuid import UUID
from datetime import datetime

from habit_tracker.domain import Streak


streak = Streak(habit_id=UUID(int=1), count=3, last_completed_at=datetime(2023, 1, 1))


def test_is_at_least():
    assert streak.is_at_least(3)
    assert not streak.is_at_least(4)


def test_is_at_least_raises():
    with pytest.raises(ValueError):
        streak.is_at_least(-1)
