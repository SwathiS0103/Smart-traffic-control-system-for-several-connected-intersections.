from typing import Dict, List, Optional
from .event_models import Event, EventStatus

class EventEngine:
    """Core orchestrator for the event lifecycle."""
    
    def __init__(self):
        self._events: Dict[str, Event] = {}

    def add_event(self, event: Event) -> None:
        """Add a new event to the engine."""
        self._events[event.event_id] = event

    def activate_event(self, event_id: str) -> None:
        """Mark an event as ACTIVE."""
        if event_id in self._events:
            self._events[event_id].status = EventStatus.ACTIVE

    def resolve_event(self, event_id: str) -> None:
        """Mark an event as RESOLVED."""
        if event_id in self._events:
            self._events[event_id].status = EventStatus.RESOLVED

    def remove_event(self, event_id: str) -> None:
        """Remove an event completely from the engine."""
        if event_id in self._events:
            del self._events[event_id]

    def get_event(self, event_id: str) -> Optional[Event]:
        """Retrieve an event by ID."""
        return self._events.get(event_id)

    def get_active_events(self) -> List[Event]:
        """Return all currently ACTIVE events."""
        return [e for e in self._events.values() if e.status == EventStatus.ACTIVE]

    def update_event(self, event_id: str, **kwargs) -> None:
        """Update fields on an existing event."""
        event = self.get_event(event_id)
        if not event:
            return
            
        for key, value in kwargs.items():
            if hasattr(event, key):
                setattr(event, key, value)
            elif key in event.details:
                event.details[key] = value
            else:
                event.details[key] = value

    def process_events(self, traffic_state: dict) -> None:
        """
        Evaluate traffic state and existing events to transition states.
        This will be expanded later to integrate with CongestionDetector, etc.
        """
        # For now, a placeholder logic.
        # Check active events to see if they've exceeded duration (if duration provided)
        current_time = traffic_state.get("timestamp", 0)
        
        for event in self.get_active_events():
            if event.duration and current_time >= event.start_time + event.duration:
                self.resolve_event(event.event_id)
