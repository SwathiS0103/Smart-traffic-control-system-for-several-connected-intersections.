from fastapi import FastAPI, HTTPException
from typing import Dict, Any, List
from .event_engine import EventEngine
from .event_models import Event, EmergencyVehicle
from .integration_adapter import IntegrationAdapter

app = FastAPI(title="Q-FLOW Dynamic Event Management", version="1.0.0")

# In a real app, these would be managed by a dependency injection or a service locator
engine = EventEngine()

@app.get("/health")
def read_health():
    return {"status": "Event Engine is running"}

@app.get("/events")
def get_all_events():
    return [e.model_dump() for e in engine._events.values()]

@app.get("/events/active")
def get_active_events():
    return [e.model_dump() for e in engine.get_active_events()]

@app.post("/events")
def create_event(event: Event):
    engine.add_event(event)
    return {"status": "created", "event_id": event.event_id}

@app.post("/events/{event_id}/activate")
def activate_event(event_id: str):
    engine.activate_event(event_id)
    return {"status": "activated"}

@app.post("/events/{event_id}/resolve")
def resolve_event(event_id: str):
    engine.resolve_event(event_id)
    return {"status": "resolved"}

# Member 2 Optimizer Request Generation (Mocking full orchestration)
@app.post("/optimizer/request")
def generate_optimization_request(traffic_state: Dict[str, Any]):
    # Typically this would go through all managers. 
    # For now we just use the adapter to show the schema.
    # In a full flow, this endpoint aggregates weights, active events, and routes.
    req = IntegrationAdapter.build_optimizer_request(
        traffic_state=traffic_state,
        active_events=engine.get_active_events(),
        weights={"waiting": 0.25, "queue": 0.25, "congestion": 0.20, "emergency": 0.05, "fuel": 0.1, "co2": 0.1, "throughput": 0.05}
    )
    return req
