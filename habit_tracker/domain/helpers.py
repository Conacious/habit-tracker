from __future__ import annotations
from typing import Sequence
from .completion import Completion


def _find_last_completion(
    completions: Sequence[Completion],
) -> Completion | None:
    # Find the most recent completion (the one with the largest completed_at)
    # How the lambda works:
    #   - lambda c: c.completed_at
    #   - max() will return the element with the largest value for this key
    if not completions:
        return None

    return max(completions, key=lambda c: c.completed_at)


def _find_first_completion(
    completions: Sequence[Completion],
) -> Completion | None:
    if not completions:
        return None

    return min(completions, key=lambda c: c.completed_at)
