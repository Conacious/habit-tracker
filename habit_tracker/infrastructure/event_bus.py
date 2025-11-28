from __future__ import annotations

from typing import Dict, List, Type

from habit_tracker.domain.events import DomainEvent
from habit_tracker.application.event_bus import EventBus, EventHandler


class InMemoryEventBus(EventBus):
    """Simple in-process event bus.

    - Subscribers are stored in a dict, keyed by event type.
    - When an event is published, we call all handlers subscribed for its exact type.
    """

    def __init__(self) -> None:
        # Example: { HabitCompleted: [handler1, handler2], HabitCreated: [handler3] }
        self._subscribers: Dict[Type[DomainEvent], List[EventHandler]] = {}

    def subscribe(self, event_type: Type[DomainEvent], handler: EventHandler) -> None:
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
        self._subscribers: Dict[Type[DomainEvent], List[EventHandler]] = {}

    def subscribe(self, event_type: Type[DomainEvent], handler: EventHandler) -> None:
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
