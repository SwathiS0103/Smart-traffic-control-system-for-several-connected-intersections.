from typing import Dict, List
from .event_models import Event, EventType

class WeightManager:
    """Generates dynamic optimizer weights based on active conditions."""
    
    def __init__(self):
        self.default_weights = {
            "waiting": 0.25,
            "queue": 0.25,
            "congestion": 0.20,
            "emergency": 0.05,
            "fuel": 0.10,
            "co2": 0.10,
            "throughput": 0.05
        }

    def calculate_weights(self, active_events: List[Event]) -> Dict[str, float]:
        """Adjust weights depending on the highest priority event active."""
        if not active_events:
            return self.default_weights.copy()
            
        # Determine active types
        types = {e.type for e in active_events}
        
        if EventType.EMERGENCY in types:
            return {
                "waiting": 0.10,
                "queue": 0.10,
                "congestion": 0.10,
                "emergency": 0.40,  # Huge priority to emergency
                "fuel": 0.05,
                "co2": 0.05,
                "throughput": 0.20
            }
            
        if EventType.ROAD_CLOSURE in types or EventType.ACCIDENT in types:
            return {
                "waiting": 0.15,
                "queue": 0.35,  # Focus on clearing queues
                "congestion": 0.30, # Focus on congestion relief
                "emergency": 0.05,
                "fuel": 0.05,
                "co2": 0.05,
                "throughput": 0.05
            }
            
        if EventType.PEDESTRIAN_SURGE in types:
            return {
                "waiting": 0.15,
                "queue": 0.15,
                "congestion": 0.10,
                "emergency": 0.05,
                "fuel": 0.05,
                "co2": 0.05,
                "throughput": 0.45  # Indirectly benefits pedestrians via cycle throughput
            }
            
        # Fallback to default if just general congestion
        return self.default_weights.copy()
