from typing import Dict, Any, List
from .event_models import Event, EventType, EmergencyVehicle

class IntegrationAdapter:
    """Handles data transformation between modules."""

    @staticmethod
    def build_optimizer_request(
        traffic_state: Dict[str, Any], 
        active_events: List[Event], 
        weights: Dict[str, float],
        active_emergencies: List[EmergencyVehicle] = None,
        green_corridors: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Format an optimization request for Member 2 (Quantum Optimizer)."""
        
        req = {
            "traffic_state": traffic_state,
            "active_events": [e.model_dump() for e in active_events],
            "weights": weights
        }
        
        # Inject emergency specifics if any
        if active_emergencies and green_corridors:
            emergency_data = []
            for veh in active_emergencies:
                veh_corridor = green_corridors.get(veh.vehicle_id)
                emergency_data.append({
                    "vehicle_id": veh.vehicle_id,
                    "route": veh.route,
                    "corridor": veh_corridor
                })
            req["emergency"] = emergency_data
            
        # Inject closure specifics if any
        closures = [e for e in active_events if e.type == EventType.ROAD_CLOSURE]
        if closures:
            req["closures"] = [
                {"edge": c.location, "severity": c.severity.value} for c in closures
            ]
            
        return req

    @staticmethod
    def parse_traffic_state(raw_state: Dict[str, Any]) -> Dict[str, Any]:
        """Adapter for Member 1 Traffic State input."""
        # For now, it just passes it through, but it ensures compatibility 
        # between the mock format and the real SUMO format later.
        return raw_state
