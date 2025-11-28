# Event Bus Architecture

The Habit Tracker project uses a **Pub/Sub Event Bus** to decouple the core application logic from side effects and auxiliary actions. This design allows the system to be more maintainable, testable, and extensible.

## Overview

In a Domain-Driven Design (DDD) context, **Domain Events** represent something interesting that happened in the domain. By publishing these events, we allow other parts of the system to react without tight coupling.

For example, when a habit is completed:
1.  The `Habit` entity records the completion.
2.  The `HabitTrackerService` persists the change.
3.  A `HabitCompleted` event is published.
4.  Subscribers (e.g., notification service, gamification logic) receive the event and act accordingly.

## Components

### 1. Domain Events (`habit_tracker.domain.events`)

All events inherit from the base `DomainEvent` class, which is an immutable data class containing metadata like `occurred_at`.

```python
@dataclass(frozen=True)
class DomainEvent:
    occurred_at: datetime
```

Specific events carry payload data relevant to the event:

```python
@dataclass(frozen=True)
class HabitCompleted(DomainEvent):
    habit_id: UUID
    completed_at: datetime
```

### 2. Event Bus Interface (`habit_tracker.application.event_bus`)

The `EventBus` is defined as a Protocol (interface), ensuring that the application layer doesn't depend on a specific implementation (like Redis, RabbitMQ, or in-memory).

```python
class EventBus(Protocol):
    def publish(self, event: DomainEvent) -> None:
        ...

    def subscribe(self, event_type: Type[DomainEvent], handler: EventHandler) -> None:
        ...
```

### 3. In-Memory Implementation (`habit_tracker.infrastructure.event_bus`)

For the current version of the application, we use a synchronous `InMemoryEventBus`. This implementation executes handlers immediately when an event is published, within the same process and thread.

**Note:** Since it is in-memory, events are lost if the application crashes before handlers complete, and it does not support distributed systems.

## Usage

### Defining a New Event

Add a new data class in `habit_tracker/domain/events.py`:

```python
@dataclass(frozen=True)
class StreakMilestoneReached(DomainEvent):
    habit_id: UUID
    streak_count: int
```

### Subscribing to an Event

Register a handler function with the event bus. A handler is any callable that takes the event as a single argument.

```python
def on_streak_milestone(event: StreakMilestoneReached) -> None:
    print(f"Wow! Streak of {event.streak_count} for habit {event.habit_id}")

# In your startup/configuration code:
event_bus.subscribe(StreakMilestoneReached, on_streak_milestone)
```

### Publishing an Event

Inject the `EventBus` into your service or handler and call `publish`.

```python
event = StreakMilestoneReached(
    occurred_at=datetime.now(),
    habit_id=habit.id,
    streak_count=10
)
event_bus.publish(event)
```
