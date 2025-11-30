from __future__ import annotations

from .events import DomainEvent


class EventCollector:
    def __init__(self) -> None:
        self._events: list[DomainEvent] = []

    def collect(self, event: DomainEvent) -> None:
        self._events.append(event)

    @property
    def events(self) -> list[DomainEvent]:
        return self._events[:]
