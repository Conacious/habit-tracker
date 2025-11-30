from __future__ import annotations

from collections.abc import Callable
from typing import Protocol, TypeVar

from habit_tracker.domain.events import DomainEvent

E = TypeVar("E", bound=DomainEvent)

# A handler is just "a function that takes an event and returns None"
EventHandler = Callable[[DomainEvent], None]


class EventBus(Protocol):
    """Simple pub-sub interface for domain events."""

    def publish(self, event: DomainEvent) -> None:
        """Publish a single event to all subscribers interested in its type."""
        ...

    def subscribe(self, event_type: type[E], handler: Callable[[E], None]) -> None:
        """Subscribe a handler to a specific event type."""
        ...
