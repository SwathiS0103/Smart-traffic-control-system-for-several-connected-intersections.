import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.event_engine import EventEngine
from src.event_models import Event, EventType, EventSeverity, EventStatus

def test_event_lifecycle():
    engine = EventEngine()
    
    # 1. Add event
    e = Event(event_id="TEST_1", type=EventType.CONGESTION, location="J2", severity=EventSeverity.HIGH, start_time=100)
    engine.add_event(e)
    assert engine.get_event("TEST_1") is not None
    assert engine.get_event("TEST_1").status == EventStatus.PENDING
    
    # 2. Activate event
    engine.activate_event("TEST_1")
    assert engine.get_event("TEST_1").status == EventStatus.ACTIVE
    assert len(engine.get_active_events()) == 1
    
    # 3. Resolve event
    engine.resolve_event("TEST_1")
    assert engine.get_event("TEST_1").status == EventStatus.RESOLVED
    assert len(engine.get_active_events()) == 0
    
    # 4. Remove event
    engine.remove_event("TEST_1")
    assert engine.get_event("TEST_1") is None
