from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from habit_tracker.application.event_bus import EventBus
from habit_tracker.domain.events import DomainEvent

E = TypeVar("E", bound=DomainEvent)


class InMemoryEventBus(EventBus):
    """Simple in-process event bus.

    - Subscribers are stored in a dict, keyed by event type.
    - When an event is published, we call all handlers subscribed for its exact type.
    """

    def __init__(self) -> None:
        # Example: { HabitCompleted: [handler1, handler2], HabitCreated: [handler3] }
        self._subscribers: dict[type[DomainEvent], list[Any]] = {}

    def subscribe(self, event_type: type[E], handler: Callable[[E], None]) -> None:
        handlers = self._subscribers.get(event_type)
        if handlers is None:
            handlers = []
            self._subscribers[event_type] = handlers
        handlers.append(handler)

    def publish(self, event: DomainEvent) -> None:
        event_type = type(event)
        handlers = self._subscribers.get(event_type, [])

        # Call all handlers; if one fails, we let the exception bubble up.
        for handler in handlers:
            handler(event)


class SafeInMemoryEventBus(EventBus):
    def __init__(self) -> None:
        self._subscribers: dict[type[DomainEvent], list[Any]] = {}

    def subscribe(self, event_type: type[E], handler: Callable[[E], None]) -> None:
        handlers = self._subscribers.get(event_type)
        if handlers is None:
            handlers = []
            self._subscribers[event_type] = handlers
        handlers.append(handler)

    def publish(self, event: DomainEvent) -> None:
        event_type = type(event)
        handlers = self._subscribers.get(event_type, [])

        # Call all handlers; if one fails, we let the exception bubble up.
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"Error in handler {handler}: {e}")
