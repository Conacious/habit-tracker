from __future__ import annotations

from typing import Protocol, Callable, Dict, List, Type
from habit_tracker.domain.events import DomainEvent


# A handler is just "a function that takes an event and returns None"
EventHandler = Callable[[DomainEvent], None]


class EventBus(Protocol):
    """Simple pub-sub interface for domain events."""

    def publish(self, event: DomainEvent) -> None:
        """Publish a single event to all subscribers interested in its type."""
        ...

    def subscribe(self, event_type: Type[DomainEvent], handler: EventHandler) -> None:
        """Subscribe a handler to a specific event type."""
        ...
