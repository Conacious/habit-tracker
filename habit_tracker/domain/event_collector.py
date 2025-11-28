from __future__ import annotations
from typing import List

from .events import DomainEvent


class EventCollector:
    def __init__(self) -> None:
        self._events: List[DomainEvent] = []

    def collect(self, event: DomainEvent) -> None:
        self._events.append(event)

    @property
    def events(self) -> List[DomainEvent]:
        return self._events[:]
